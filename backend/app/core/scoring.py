"""Fantasy scoring calculations."""

from typing import Dict, Any
import json


def calculate_fantasy_points(stats: Dict[str, Any], scoring_config: str) -> float:
    """
    Calculate fantasy points from player stats using scoring configuration.
    
    Args:
        stats: Dictionary of player stats (pass_yd, rush_yd, rec, etc.)
        scoring_config: JSON string of scoring rules
        
    Returns:
        Total fantasy points
    """
    scoring = json.loads(scoring_config)
    points = 0.0
    
    for stat, value in stats.items():
        if stat in scoring:
            points += value * scoring[stat]
    
    return round(points, 2)


def get_default_scoring() -> Dict[str, float]:
    """Get default PPR scoring configuration."""
    return {
        "pass_yd": 0.04,
        "pass_td": 4,
        "int": -2,
        "rush_yd": 0.1,
        "rush_td": 6,
        "rec": 1,
        "rec_yd": 0.1,
        "rec_td": 6,
        "fumble": -2
    }