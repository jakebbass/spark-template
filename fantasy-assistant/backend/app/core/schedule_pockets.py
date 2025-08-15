"""Schedule analysis and startable weeks calculation."""

from typing import Dict, Any, List
import numpy as np


def analyze_schedule_pockets(player: Dict[str, Any], season_week: int = 1) -> Dict[str, Any]:
    """
    Analyze a player's schedule to find startable weeks and early-season value.
    
    Args:
        player: Player dictionary with team and position info
        season_week: Current week of season (1-17)
        
    Returns:
        Dictionary with startable weeks analysis
    """
    team = player.get("team", "")
    position = player.get("position", "")
    fantasy_points = player.get("fantasy_points", 0)
    
    # Defense vs Position (DVP) rankings - placeholder data
    # In a real implementation, this would come from an external API or database
    dvp_rankings = _get_dvp_rankings()
    
    # Team schedule strength - placeholder implementation
    schedule_strength = _get_schedule_strength(team)
    
    # Calculate weekly startability based on:
    # 1. Player's projected usage/points
    # 2. Opponent defense strength vs position
    # 3. Game script factors
    
    startable_weeks = []
    early_season_value = 0
    
    for week in range(1, 18):  # NFL weeks 1-17
        # Base startability score
        base_score = min(fantasy_points / 17, 20)  # Points per week, capped at 20
        
        # Adjust for opponent defense
        opp_defense_rank = schedule_strength.get(week, 16)  # Default middle-tier defense
        defense_multiplier = _get_defense_multiplier(position, opp_defense_rank)
        
        weekly_score = base_score * defense_multiplier
        
        # Determine if player is startable this week
        if _is_startable(weekly_score, position):
            startable_weeks.append(week)
            
            # Add to early season value (weeks 1-4)
            if week <= 4:
                early_season_value += weekly_score
    
    # Calculate schedule pocket metrics
    consecutive_pockets = _find_consecutive_pockets(startable_weeks)
    best_pocket = max(consecutive_pockets, key=len) if consecutive_pockets else []
    
    return {
        "startable_weeks": startable_weeks,
        "startable_count": len(startable_weeks),
        "early_season_value": round(early_season_value, 1),
        "best_pocket": best_pocket,
        "best_pocket_length": len(best_pocket),
        "schedule_difficulty": _calculate_schedule_difficulty(schedule_strength),
        "bye_week": player.get("bye_week", None)
    }


def batch_analyze_schedules(players: List[Dict[str, Any]], season_week: int = 1) -> List[Dict[str, Any]]:
    """
    Analyze schedules for a batch of players.
    
    Args:
        players: List of player dictionaries
        season_week: Current week of season
        
    Returns:
        Updated players with schedule analysis
    """
    for player in players:
        schedule_analysis = analyze_schedule_pockets(player, season_week)
        
        # Add schedule metrics to player
        player.update({
            "schedule_startable_weeks": schedule_analysis["startable_weeks"],
            "schedule_startable_count": schedule_analysis["startable_count"],
            "schedule_early_season_value": schedule_analysis["early_season_value"],
            "schedule_best_pocket": schedule_analysis["best_pocket"],
            "schedule_difficulty": schedule_analysis["schedule_difficulty"]
        })
        
        # Add interpretive flags
        if schedule_analysis["startable_count"] >= 12:
            player["schedule_grade"] = "A"
        elif schedule_analysis["startable_count"] >= 10:
            player["schedule_grade"] = "B"
        elif schedule_analysis["startable_count"] >= 8:
            player["schedule_grade"] = "C"
        else:
            player["schedule_grade"] = "D"
    
    return players


def get_early_season_values(players: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Get players with highest early-season value (weeks 1-4).
    
    Args:
        players: List of players with schedule analysis
        top_n: Number of top early-season candidates
        
    Returns:
        List of top early-season value players
    """
    early_season_players = [
        p for p in players 
        if p.get("schedule_early_season_value", 0) > 0
    ]
    
    # Sort by early season value descending
    early_season_players.sort(key=lambda x: x.get("schedule_early_season_value", 0), reverse=True)
    
    return early_season_players[:top_n]


def _get_dvp_rankings() -> Dict[str, Dict[str, int]]:
    """Get Defense vs Position rankings - placeholder data."""
    # In a real implementation, this would be updated weekly from external data
    return {
        "QB": {"BUF": 1, "BAL": 5, "KC": 10, "SF": 8, "DAL": 12, "MIA": 15, "PHI": 7, "GB": 18, "CIN": 14, "IND": 20, "LV": 25, "MIN": 22, "ATL": 28, "DET": 16, "TEN": 30, "LAC": 11, "NYJ": 6, "CLE": 13, "NO": 19, "CHI": 24},
        "RB": {"BUF": 8, "BAL": 12, "KC": 15, "SF": 6, "DAL": 18, "MIA": 22, "PHI": 10, "GB": 25, "CIN": 20, "IND": 14, "LV": 28, "MIN": 16, "ATL": 30, "DET": 24, "TEN": 26, "LAC": 9, "NYJ": 11, "CLE": 7, "NO": 19, "CHI": 21},
        "WR": {"BUF": 12, "BAL": 8, "KC": 20, "SF": 10, "DAL": 25, "MIA": 14, "PHI": 15, "GB": 28, "CIN": 22, "IND": 18, "LV": 30, "MIN": 24, "ATL": 26, "DET": 16, "TEN": 27, "LAC": 13, "NYJ": 6, "CLE": 11, "NO": 17, "CHI": 5},
        "TE": {"BUF": 18, "BAL": 10, "KC": 22, "SF": 12, "DAL": 28, "MIA": 20, "PHI": 14, "GB": 30, "CIN": 24, "IND": 16, "LV": 26, "MIN": 25, "ATL": 29, "DET": 19, "TEN": 27, "LAC": 15, "NYJ": 8, "CLE": 13, "NO": 21, "CHI": 7}
    }


def _get_schedule_strength(team: str) -> Dict[int, int]:
    """Get schedule strength for a team by week - placeholder implementation."""
    # In a real implementation, this would be based on actual NFL schedules
    # Return random-ish difficulty for demo purposes
    np.random.seed(hash(team) % 2**32)  # Consistent per team
    return {week: max(1, min(32, int(np.random.normal(16, 8)))) for week in range(1, 18)}


def _get_defense_multiplier(position: str, defense_rank: int) -> float:
    """Calculate multiplier based on opponent defense strength."""
    # Lower defense rank = stronger defense = lower multiplier
    # Rank 1 = best defense (0.8x), Rank 32 = worst defense (1.2x)
    base_multiplier = 1.0
    
    if defense_rank <= 5:  # Top 5 defenses
        base_multiplier = 0.8
    elif defense_rank <= 10:  # Top 10
        base_multiplier = 0.9
    elif defense_rank <= 20:  # Average
        base_multiplier = 1.0
    elif defense_rank <= 27:  # Below average
        base_multiplier = 1.1
    else:  # Bottom 5
        base_multiplier = 1.2
    
    return base_multiplier


def _is_startable(weekly_score: float, position: str) -> bool:
    """Determine if a player is startable based on weekly projected score."""
    # Position-specific startable thresholds
    thresholds = {
        "QB": 18,   # ~QB12 level
        "RB": 12,   # ~RB24 level  
        "WR": 10,   # ~WR36 level
        "TE": 8     # ~TE12 level
    }
    
    threshold = thresholds.get(position, 10)
    return weekly_score >= threshold


def _find_consecutive_pockets(startable_weeks: List[int]) -> List[List[int]]:
    """Find consecutive stretches of startable weeks."""
    if not startable_weeks:
        return []
    
    pockets = []
    current_pocket = [startable_weeks[0]]
    
    for i in range(1, len(startable_weeks)):
        if startable_weeks[i] == startable_weeks[i-1] + 1:
            current_pocket.append(startable_weeks[i])
        else:
            if len(current_pocket) >= 2:  # Only consider pockets of 2+ weeks
                pockets.append(current_pocket)
            current_pocket = [startable_weeks[i]]
    
    # Don't forget the last pocket
    if len(current_pocket) >= 2:
        pockets.append(current_pocket)
    
    return pockets


def _calculate_schedule_difficulty(schedule_strength: Dict[int, int]) -> str:
    """Calculate overall schedule difficulty rating."""
    avg_strength = np.mean(list(schedule_strength.values()))
    
    if avg_strength <= 12:
        return "Easy"
    elif avg_strength <= 18:
        return "Average"
    else:
        return "Difficult"