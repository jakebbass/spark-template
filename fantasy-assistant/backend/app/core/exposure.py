"""Exposure control for multi-league management."""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func


class ExposureTracker:
    """Track player exposure across multiple leagues for a user."""
    
    def __init__(self, user_id: str, db: AsyncSession):
        self.user_id = user_id
        self.db = db
        self.exposure_limits = {
            "QB": {"max_percentage": 40, "max_leagues": 2},
            "RB": {"max_percentage": 30, "max_leagues": 3}, 
            "WR": {"max_percentage": 25, "max_leagues": 4},
            "TE": {"max_percentage": 35, "max_leagues": 2}
        }
    
    def set_exposure_limits(self, limits: Dict[str, Dict[str, float]]):
        """Set custom exposure limits for the user."""
        self.exposure_limits.update(limits)
    
    async def get_current_exposure(self, player_id: str) -> Dict[str, Any]:
        """Get current exposure for a specific player."""
        from app.db.models import DraftPick, Player
        
        # Get all leagues this user has picks in
        user_leagues_query = select(DraftPick.league_id).distinct().where(
            DraftPick.league_id.like(f"{self.user_id}_%")  # Assuming league_id format includes user_id
        )
        user_leagues_result = await self.db.execute(user_leagues_query)
        user_leagues = [row[0] for row in user_leagues_result.all()]
        
        if not user_leagues:
            return {"leagues_with_player": 0, "total_leagues": 0, "exposure_percentage": 0}
        
        # Count leagues where user has this player
        player_leagues_query = select(func.count(DraftPick.league_id.distinct())).where(
            (DraftPick.player_id == player_id) &
            (DraftPick.league_id.in_(user_leagues))
        )
        player_leagues_result = await self.db.execute(player_leagues_query)
        leagues_with_player = player_leagues_result.scalar() or 0
        
        exposure_percentage = (leagues_with_player / len(user_leagues)) * 100 if user_leagues else 0
        
        return {
            "leagues_with_player": leagues_with_player,
            "total_leagues": len(user_leagues),
            "exposure_percentage": round(exposure_percentage, 1)
        }
    
    async def is_overexposed(self, player_id: str, position: str) -> bool:
        """Check if adding this player would create overexposure."""
        current_exposure = await self.get_current_exposure(player_id)
        position_limits = self.exposure_limits.get(position, {"max_percentage": 30})
        
        max_percentage = position_limits.get("max_percentage", 30)
        
        return current_exposure["exposure_percentage"] >= max_percentage
    
    async def get_exposure_warnings(self, player_recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get exposure warnings for a list of player recommendations."""
        warnings = []
        
        for player in player_recommendations:
            player_id = player.get("id")
            position = player.get("position")
            
            if not player_id or not position:
                continue
            
            current_exposure = await self.get_current_exposure(player_id)
            position_limits = self.exposure_limits.get(position, {"max_percentage": 30})
            
            max_percentage = position_limits.get("max_percentage", 30)
            current_percentage = current_exposure["exposure_percentage"]
            
            if current_percentage >= max_percentage:
                warnings.append({
                    "player": player,
                    "warning_type": "overexposed",
                    "current_exposure": current_percentage,
                    "limit": max_percentage,
                    "message": f"{player['name']} is at {current_percentage}% exposure (limit: {max_percentage}%)"
                })
            elif current_percentage >= max_percentage * 0.8:  # 80% of limit
                warnings.append({
                    "player": player,
                    "warning_type": "approaching_limit",
                    "current_exposure": current_percentage,
                    "limit": max_percentage,
                    "message": f"{player['name']} approaching exposure limit ({current_percentage}%/{max_percentage}%)"
                })
        
        return warnings
    
    async def get_exposure_alternatives(self, overexposed_player: Dict[str, Any], available_players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find alternative players when the preferred choice is overexposed."""
        position = overexposed_player.get("position")
        overexposed_vorp = overexposed_player.get("vorp", 0)
        
        # Find players of same position with similar or better VORP
        alternatives = []
        for player in available_players:
            if (player.get("position") == position and 
                player.get("id") != overexposed_player.get("id") and
                player.get("vorp", 0) >= overexposed_vorp * 0.8):  # Within 80% of original VORP
                
                # Check if this alternative would also be overexposed
                is_alt_overexposed = await self.is_overexposed(player["id"], position)
                
                if not is_alt_overexposed:
                    exposure_info = await self.get_current_exposure(player["id"])
                    player_with_exposure = player.copy()
                    player_with_exposure.update({
                        "exposure_percentage": exposure_info["exposure_percentage"],
                        "reason": f"Alternative to overexposed {overexposed_player['name']}"
                    })
                    alternatives.append(player_with_exposure)
        
        # Sort alternatives by VORP descending
        alternatives.sort(key=lambda x: x.get("vorp", 0), reverse=True)
        
        return alternatives[:3]  # Return top 3 alternatives


def apply_exposure_control(recommendations: List[Dict[str, Any]], exposure_tracker: ExposureTracker) -> List[Dict[str, Any]]:
    """Apply exposure control to player recommendations."""
    # This would be called asynchronously in the advice endpoint
    # For now, return a placeholder implementation
    
    controlled_recommendations = []
    for rec in recommendations:
        player = rec.get("player", {})
        position = player.get("position", "")
        
        # Add exposure context (placeholder values)
        rec["exposure_info"] = {
            "current_percentage": 15.0,  # Placeholder
            "is_overexposed": False,
            "within_limits": True
        }
        
        controlled_recommendations.append(rec)
    
    return controlled_recommendations


def get_diversification_suggestions(user_positions: Dict[str, int], available_players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Suggest players to improve portfolio diversification."""
    suggestions = []
    
    # Find underrepresented positions
    position_counts = {"QB": 0, "RB": 0, "WR": 0, "TE": 0}
    position_counts.update(user_positions)
    
    # Calculate position needs based on typical roster construction
    typical_roster = {"QB": 2, "RB": 4, "WR": 5, "TE": 2}
    
    for position, typical_count in typical_roster.items():
        current_count = position_counts.get(position, 0)
        if current_count < typical_count:
            # Find best available players at this position
            pos_players = [p for p in available_players if p.get("position") == position]
            if pos_players:
                best_pos_player = max(pos_players, key=lambda x: x.get("vorp", 0))
                suggestions.append({
                    "position": position,
                    "player": best_pos_player,
                    "reason": f"Diversify portfolio - only {current_count}/{typical_count} {position}s",
                    "priority": typical_count - current_count
                })
    
    return sorted(suggestions, key=lambda x: x["priority"], reverse=True)


# Legacy functions for compatibility
def check_exposure_limits(
    player_id: str, 
    user_id: str, 
    current_exposure: Dict[str, float],
    limits: Dict[str, float]
) -> Dict[str, Any]:
    """Legacy function - use ExposureTracker instead."""
    return {
        "exceeds_limit": False,
        "current_exposure": 0.0,
        "limit": 0.2,
        "warning": None
    }


def get_exposure_alternatives(
    overexposed_player: Dict[str, Any],
    available_players: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Legacy function - use ExposureTracker instead."""
    return []