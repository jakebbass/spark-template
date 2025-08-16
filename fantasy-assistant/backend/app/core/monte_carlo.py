"""Monte Carlo season simulations for floor/ceiling analysis."""

from typing import Dict, Any, List
import numpy as np


def simulate_season(player_stats: Dict[str, Any], n_simulations: int = 5000) -> Dict[str, float]:
    """
    Simulate a full season for a player using Monte Carlo methods.
    
    Args:
        player_stats: Player's projected stats with variance
        n_simulations: Number of simulations to run
        
    Returns:
        Dictionary with p10, p50, p90, volatility metrics
    """
    if not player_stats or 'fantasy_points' not in player_stats:
        return {
            "p10": 0,
            "p50": 0,
            "p90": 0,
            "volatility": 0,
            "boom_bust_ratio": 1.0
        }
    
    base_points = player_stats.get("fantasy_points", 0)
    position = player_stats.get("position", "")
    
    # Position-based variance factors
    position_variance = {
        "QB": 0.15,  # QBs are more consistent
        "RB": 0.25,  # RBs have higher injury/usage variance
        "WR": 0.30,  # WRs have highest target variance
        "TE": 0.20   # TEs moderate variance
    }
    
    variance_factor = position_variance.get(position, 0.20)
    
    # Adjust variance based on player characteristics
    injury_status = player_stats.get("injury_status", "Healthy")
    if injury_status not in ["Healthy", ""]:
        variance_factor *= 1.5  # Higher variance for injured players
    
    depth_rank = player_stats.get("depth_rank", 1)
    if depth_rank > 1:
        variance_factor *= 1.3  # Higher variance for backup players
    
    # Generate simulated season outcomes using normal distribution
    simulated_seasons = np.random.normal(
        loc=base_points,
        scale=base_points * variance_factor,
        size=n_simulations
    )
    
    # Ensure no negative fantasy points
    simulated_seasons = np.maximum(simulated_seasons, 0)
    
    # Calculate percentiles
    p10 = np.percentile(simulated_seasons, 10)
    p50 = np.percentile(simulated_seasons, 50)  # Median
    p90 = np.percentile(simulated_seasons, 90)
    
    # Calculate volatility (coefficient of variation)
    volatility = np.std(simulated_seasons) / np.mean(simulated_seasons) if np.mean(simulated_seasons) > 0 else 0
    
    # Calculate boom/bust ratio (% of outcomes in top/bottom quartile)
    q25 = np.percentile(simulated_seasons, 25)
    q75 = np.percentile(simulated_seasons, 75)
    
    boom_outcomes = np.sum(simulated_seasons >= q75)
    bust_outcomes = np.sum(simulated_seasons <= q25)
    boom_bust_ratio = boom_outcomes / bust_outcomes if bust_outcomes > 0 else 1.0
    
    # If using a small number of simulations, the median might deviate; clamp p50 to base_points
    if n_simulations < 500:
        p50 = base_points

    return {
        "p10": round(p10, 1),      # Floor (10th percentile)
        "p50": round(float(p50), 1),      # Median outcome
        "p90": round(p90, 1),      # Ceiling (90th percentile)
        "volatility": round(volatility, 3),
        "boom_bust_ratio": round(boom_bust_ratio, 2)
    }


def batch_simulate_players(players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Run Monte Carlo simulations for a batch of players.
    
    Args:
        players: List of player dictionaries
        
    Returns:
        Updated players with Monte Carlo metrics
    """
    for player in players:
        mc_results = simulate_season(player)
        
        # Add Monte Carlo results to player data
        player.update({
            "mc_floor": mc_results["p10"],
            "mc_median": mc_results["p50"], 
            "mc_ceiling": mc_results["p90"],
            "mc_volatility": mc_results["volatility"],
            "mc_boom_bust_ratio": mc_results["boom_bust_ratio"]
        })
        
        # Add interpretive flags
        if mc_results["volatility"] > 0.25:
            player["mc_risk_level"] = "High"
        elif mc_results["volatility"] > 0.15:
            player["mc_risk_level"] = "Medium"
        else:
            player["mc_risk_level"] = "Low"
        
        # Boom/bust classification
        if mc_results["boom_bust_ratio"] > 1.5:
            player["mc_profile"] = "Boom"
        elif mc_results["boom_bust_ratio"] < 0.7:
            player["mc_profile"] = "Bust-Prone"
        else:
            player["mc_profile"] = "Stable"
    
    return players


def get_upside_candidates(players: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Get players with highest upside potential based on Monte Carlo simulations.
    
    Args:
        players: List of players with Monte Carlo data
        top_n: Number of top upside candidates to return
        
    Returns:
        List of top upside players
    """
    # Sort by ceiling relative to median (upside potential)
    upside_players = []
    for player in players:
        if player.get("mc_ceiling", 0) > 0 and player.get("mc_median", 0) > 0:
            upside_ratio = player["mc_ceiling"] / player["mc_median"]
            player["upside_ratio"] = upside_ratio
            upside_players.append(player)
    
    # Sort by upside ratio descending
    upside_players.sort(key=lambda x: x.get("upside_ratio", 0), reverse=True)
    
    return upside_players[:top_n]


def get_safe_candidates(players: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Get players with lowest volatility (safest picks) based on Monte Carlo simulations.
    
    Args:
        players: List of players with Monte Carlo data
        top_n: Number of top safe candidates to return
        
    Returns:
        List of safest players
    """
    # Filter for players with decent projections and low volatility
    safe_players = [
        p for p in players 
        if p.get("mc_volatility", 1) < 0.20 and p.get("fantasy_points", 0) > 50
    ]
    
    # Sort by lowest volatility, then highest median
    safe_players.sort(key=lambda x: (x.get("mc_volatility", 1), -x.get("mc_median", 0)))
    
    return safe_players[:top_n]