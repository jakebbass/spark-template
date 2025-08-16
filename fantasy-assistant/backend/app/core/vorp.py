"""Value Over Replacement Player (VORP) calculations."""

from typing import List, Dict, Any
import numpy as np


def calculate_vorp(players: List[Dict[str, Any]], position_baselines: Dict[str, int] = None) -> List[Dict[str, Any]]:
    """
    Calculate VORP for each player based on positional baselines.
    
    Args:
        players: List of player dictionaries with position and fantasy_points
        position_baselines: Number of starters by position (default: QB12, RB24, WR36, TE12)
        
    Returns:
        Updated players list with vorp field added
    """
    if position_baselines is None:
        position_baselines = {
            "QB": 12,
            "RB": 24,
            "WR": 36,
            "TE": 12
        }
    
    # Calculate baselines for each position
    position_players = {}
    for player in players:
        pos = player.get("position", "")
        if pos not in position_players:
            position_players[pos] = []
        position_players[pos].append(player)
    
    # Sort by fantasy points and determine baseline
    baselines = {}
    for pos, pos_players in position_players.items():
        sorted_players = sorted(pos_players, key=lambda p: p.get("fantasy_points", 0), reverse=True)
        baseline_rank = position_baselines.get(pos, 12)
        # If there are fewer players than the requested baseline_rank, use the last player's points
        if len(sorted_players) >= baseline_rank and baseline_rank > 0:
            baselines[pos] = sorted_players[baseline_rank - 1].get("fantasy_points", 0)
        elif len(sorted_players) > 0:
            baselines[pos] = sorted_players[-1].get("fantasy_points", 0)
        else:
            baselines[pos] = 0
    
    # Calculate VORP
    for player in players:
        pos = player.get("position", "")
        fantasy_points = player.get("fantasy_points", 0)
        baseline = baselines.get(pos, 0)
    # VORP can be negative if below baseline; tests expect direct subtraction
    player["vorp"] = fantasy_points - baseline
    
    return players


def calculate_tiers(players: List[Dict[str, Any]], position: str = None) -> List[Dict[str, Any]]:
    """
    Calculate tiers using natural gap detection in VORP scores.
    
    Args:
        players: List of players with vorp values
        position: Optional position filter
        
    Returns:
        Updated players list with tier field added
    """
    filtered_players = players
    if position:
        filtered_players = [p for p in players if p.get("position") == position]
    
    # Sort by VORP descending
    sorted_players = sorted(filtered_players, key=lambda p: p.get("vorp", 0), reverse=True)
    
    if not sorted_players:
        return players
    
    # Use natural gaps to determine tiers
    gaps = []
    for i in range(len(sorted_players) - 1):
        gap = sorted_players[i].get("vorp", 0) - sorted_players[i + 1].get("vorp", 0)
        gaps.append(gap)
    
    if not gaps:
        for player in sorted_players:
            player["tier"] = 1
        return players
    
    # Find significant gaps (> mean + std)
    mean_gap = np.mean(gaps)
    std_gap = np.std(gaps)
    threshold = mean_gap + std_gap
    
    # Assign tiers
    current_tier = 1
    for i, player in enumerate(sorted_players):
        player["tier"] = current_tier
        if i < len(gaps) and gaps[i] > threshold:
            current_tier += 1
    
    return players