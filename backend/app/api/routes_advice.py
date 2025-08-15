"""Advice API routes."""

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List, Dict, Any
import json
import redis

from app.db.base import get_db
from app.db.models import Player, Projection, DraftPick, Injury, ADP, DepthChart
from app.core.scoring import calculate_fantasy_points, get_default_scoring
from app.core.vorp import calculate_vorp, calculate_tiers
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def get_advice(
    league_id: str = Query(..., description="League identifier"),
    round: int = Query(..., description="Current draft round"),
    pick: int = Query(..., description="Pick number in round"),
    roster_state: Optional[str] = Query(None, description="JSON string of current roster"),
    scoring_profile: Optional[str] = Query(None, description="Custom scoring profile"),
    strategy: Optional[str] = Query("balanced", description="Draft strategy: balanced, upside, safe"),
    db: AsyncSession = Depends(get_db)
):
    """Get AI draft recommendations and rationale."""
    
    try:
        # Get scoring configuration
        if scoring_profile:
            scoring_config = json.loads(scoring_profile)
        else:
            scoring_config = get_default_scoring()
        
        # Parse roster state
        current_roster = []
        roster_needs = {"QB": 1, "RB": 2, "WR": 3, "TE": 1}  # Default needs
        
        if roster_state:
            try:
                current_roster = json.loads(roster_state)
                # Calculate remaining needs based on current roster
                for player in current_roster:
                    pos = player.get("position", "")
                    if pos in roster_needs and roster_needs[pos] > 0:
                        roster_needs[pos] -= 1
            except json.JSONDecodeError:
                pass
        
        # Get all drafted players in this league
        drafted_query = select(DraftPick.player_id).where(DraftPick.league_id == league_id)
        drafted_result = await db.execute(drafted_query)
        drafted_player_ids = {str(row[0]) for row in drafted_result.all()}
        
        # Get available players with full data
        query = select(
            Player,
            Projection,
            Injury,
            ADP,
            DepthChart
        ).select_from(Player)\
         .outerjoin(Projection, and_(Player.id == Projection.player_id, Projection.season == 2024))\
         .outerjoin(Injury, Player.id == Injury.player_id)\
         .outerjoin(ADP, and_(Player.id == ADP.player_id, ADP.platform == 'sleeper'))\
         .outerjoin(DepthChart, Player.id == DepthChart.player_id)\
         .where(~Player.id.in_(drafted_player_ids))  # Exclude drafted players
        
        result = await db.execute(query)
        rows = result.all()
        
        # Process available players
        available_players = []
        for row in rows:
            player, projection, injury, adp, depth = row
            
            # Calculate fantasy points
            fantasy_points = 0
            if projection and projection.stats:
                fantasy_points = calculate_fantasy_points(projection.stats, json.dumps(scoring_config))
            
            player_data = {
                "id": str(player.id),
                "name": player.name,
                "team": player.team,
                "position": player.position,
                "fantasy_points": fantasy_points,
                "injury_status": injury.status if injury else "Healthy",
                "injury_note": injury.note if injury else "",
                "adp": float(adp.adp) if adp else None,
                "depth_rank": depth.rank if depth else None
            }
            
            available_players.append(player_data)
        
        if not available_players:
            return {
                "top5": [],
                "rationale": "No available players found",
                "fallbacks": []
            }
        
        # Calculate VORP and tiers for available players
        available_players = calculate_vorp(available_players)
        
        # Calculate tiers by position
        positions = set(p['position'] for p in available_players)
        for position in positions:
            available_players = calculate_tiers(available_players, position)
        
        # Generate recommendations based on strategy
        recommendations = []
        
        if strategy == "upside":
            # Prefer high-ceiling players (top tier or good VORP)
            available_players.sort(key=lambda x: (
                x.get('tier', 999),  # Lower tier number is better
                -x.get('vorp', 0)    # Higher VORP is better
            ))
        elif strategy == "safe": 
            # Prefer consistent players (good ADP, healthy)
            available_players.sort(key=lambda x: (
                1 if x.get('injury_status', 'Healthy') != 'Healthy' else 0,  # Healthy first
                x.get('adp', 999),   # Lower ADP is better (drafted earlier)
                -x.get('vorp', 0)    # Higher VORP as tiebreaker
            ))
        else:  # balanced
            # Balance value and need
            available_players.sort(key=lambda x: (
                0 if x.get('position') in [pos for pos, need in roster_needs.items() if need > 0] else 1,
                -x.get('vorp', 0),
                x.get('tier', 999)
            ))
        
        # Generate top 5 recommendations
        top5 = []
        for i, player in enumerate(available_players[:5]):
            # Calculate recommendation score
            score = _calculate_recommendation_score(player, roster_needs, strategy)
            
            recommendation = {
                "rank": i + 1,
                "player": player,
                "score": score,
                "reasoning": _generate_reasoning(player, roster_needs, strategy, round)
            }
            top5.append(recommendation)
        
        # Generate fallback options (next 5 players by position need)
        fallbacks = []
        needed_positions = [pos for pos, need in roster_needs.items() if need > 0]
        
        for pos in needed_positions:
            pos_players = [p for p in available_players if p['position'] == pos]
            if pos_players:
                best_pos_player = pos_players[0]
                if best_pos_player['id'] not in [r['player']['id'] for r in top5]:
                    fallbacks.append({
                        "position": pos,
                        "player": best_pos_player,
                        "reasoning": f"Best available {pos} to fill roster need"
                    })
        
        # Generate overall rationale
        rationale = _generate_overall_rationale(top5, roster_needs, strategy, round, pick)
        
        return {
            "top5": top5,
            "rationale": rationale,
            "fallbacks": fallbacks[:3],  # Limit to 3 fallbacks
            "roster_needs": roster_needs,
            "strategy": strategy,
            "context": {
                "round": round,
                "pick": pick,
                "available_count": len(available_players)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advice: {str(e)}")


def _calculate_recommendation_score(player: Dict[str, Any], roster_needs: Dict[str, int], strategy: str) -> float:
    """Calculate a recommendation score for a player."""
    base_score = player.get('vorp', 0)
    
    # Position need bonus
    if player.get('position') in [pos for pos, need in roster_needs.items() if need > 0]:
        base_score += 20
    
    # Strategy adjustments
    if strategy == "upside":
        # Bonus for tier 1 players
        if player.get('tier', 999) == 1:
            base_score += 15
    elif strategy == "safe":
        # Penalty for injury concerns
        if player.get('injury_status', 'Healthy') != 'Healthy':
            base_score -= 25
        # Bonus for good ADP (consensus pick)
        if player.get('adp') and player.get('adp') < 50:
            base_score += 10
    
    return round(base_score, 1)


def _generate_reasoning(player: Dict[str, Any], roster_needs: Dict[str, int], strategy: str, round: int) -> str:
    """Generate reasoning for a player recommendation."""
    reasons = []
    
    # Position need
    if player.get('position') in [pos for pos, need in roster_needs.items() if need > 0]:
        reasons.append(f"fills {player['position']} need")
    
    # Value assessment
    vorp = player.get('vorp', 0)
    if vorp > 50:
        reasons.append("excellent value")
    elif vorp > 20:
        reasons.append("good value")
    
    # Tier information
    tier = player.get('tier', 999)
    if tier == 1:
        reasons.append("tier 1 player")
    elif tier == 2:
        reasons.append("tier 2 player")
    
    # Injury concerns
    if player.get('injury_status') not in ['Healthy', '']:
        reasons.append(f"injury concern ({player.get('injury_status')})")
    
    # ADP context
    adp = player.get('adp')
    if adp:
        if adp < round * 12:  # Assuming 12-team league
            reasons.append("falling below ADP")
        elif adp > (round + 2) * 12:
            reasons.append("ahead of ADP")
    
    if not reasons:
        reasons.append("solid option")
    
    return f"{player['name']}: " + ", ".join(reasons)


def _generate_overall_rationale(top5: List[Dict], roster_needs: Dict[str, int], strategy: str, round: int, pick: int) -> str:
    """Generate overall draft advice rationale."""
    if not top5:
        return "No recommendations available."
    
    top_pick = top5[0]
    
    rationale_parts = [
        f"Round {round}, Pick {pick}:",
        f"Top recommendation is {top_pick['player']['name']} ({top_pick['player']['position']})."
    ]
    
    # Strategy context
    if strategy == "upside":
        rationale_parts.append("Focusing on high-ceiling players for maximum potential.")
    elif strategy == "safe":
        rationale_parts.append("Prioritizing consistent, low-risk players.")
    else:
        rationale_parts.append("Balancing value and roster construction.")
    
    # Need context
    urgent_needs = [pos for pos, need in roster_needs.items() if need > 0]
    if urgent_needs:
        rationale_parts.append(f"Roster needs: {', '.join(urgent_needs)}.")
    
    return " ".join(rationale_parts)