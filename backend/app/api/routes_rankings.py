"""Rankings API routes."""

from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Dict, Any
import json

from app.db.base import get_db
from app.db.models import Player, Projection, HistoricalStats, Injury, ADP, DepthChart
from app.core.scoring import calculate_fantasy_points, get_default_scoring
from app.core.vorp import calculate_vorp, calculate_tiers
from app.core.monte_carlo import batch_simulate_players
from app.core.schedule_pockets import batch_analyze_schedules

router = APIRouter()


@router.get("/")
async def get_rankings(
    pos: Optional[str] = Query(None, description="Position filter (QB, RB, WR, TE)"),
    limit: int = Query(250, description="Number of players to return"),
    scoring_profile: Optional[str] = Query(None, description="Custom scoring profile"),
    db: AsyncSession = Depends(get_db)
):
    """Get player rankings with projections, VORP, tiers, and advanced metrics."""
    
    try:
        # Get scoring configuration
        if scoring_profile:
            scoring_config = json.loads(scoring_profile)
        else:
            scoring_config = get_default_scoring()
        
        # Build base query with joins
        query = select(
            Player,
            Projection,
            HistoricalStats,
            Injury,
            ADP,
            DepthChart
        ).select_from(Player)\
         .outerjoin(Projection, (Player.id == Projection.player_id) & (Projection.season == 2024))\
         .outerjoin(HistoricalStats, (Player.id == HistoricalStats.player_id) & (HistoricalStats.season == 2023))\
         .outerjoin(Injury, Player.id == Injury.player_id)\
         .outerjoin(ADP, (Player.id == ADP.player_id) & (ADP.platform == 'sleeper'))\
         .outerjoin(DepthChart, Player.id == DepthChart.player_id)
        
        # Add position filter if provided
        if pos:
            query = query.where(Player.position == pos.upper())
        
        result = await db.execute(query)
        rows = result.all()
        
        # Process results
        players = []
        for row in rows:
            player, projection, historical, injury, adp, depth = row
            
            # Calculate fantasy points from projections
            fantasy_points = 0
            if projection and projection.stats:
                fantasy_points = calculate_fantasy_points(projection.stats, json.dumps(scoring_config))
            
            # Build player data
            player_data = {
                "id": str(player.id),
                "name": player.name,
                "team": player.team,
                "position": player.position,
                "bye_week": player.bye_week,
                "fantasy_points": fantasy_points,
                "projections": projection.stats if projection else {},
                "historical_stats": historical.stats if historical else {},
                "injury_status": injury.status if injury else "Healthy",
                "injury_note": injury.note if injury else "",
                "adp": float(adp.adp) if adp else None,
                "adp_sample_size": adp.sample_size if adp else None,
                "depth_rank": depth.rank if depth else None,
                "sleeper_id": player.xrefs.get('sleeper_id') if player.xrefs else None
            }
            
            players.append(player_data)
        
        # Calculate VORP and tiers
        if players:
            players = calculate_vorp(players)
            
            # Calculate tiers by position
            positions = set(p['position'] for p in players)
            for position in positions:
                players = calculate_tiers(players, position)
            
            # Add Monte Carlo simulations
            players = batch_simulate_players(players)
            
            # Add schedule analysis
            players = batch_analyze_schedules(players)
        
        # Sort by VORP descending, then fantasy points descending
        players.sort(key=lambda x: (x.get('vorp', 0), x.get('fantasy_points', 0)), reverse=True)
        
        # Apply limit
        players = players[:limit]
        
        return {
            "players": players,
            "total": len(players),
            "scoring": scoring_config,
            "filters": {
                "position": pos,
                "limit": limit
            }
        }
        
    except Exception as e:
        return {
            "players": [],
            "total": 0,
            "error": f"Error fetching rankings: {str(e)}",
            "message": "Unable to fetch rankings"
        }