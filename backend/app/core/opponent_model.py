"""Opponent modeling for draft pick prediction."""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from collections import defaultdict


class OpponentModel:
    """Model to predict opponent draft picks."""
    
    def __init__(self, league_id: str, team_count: int = 12):
        self.league_id = league_id
        self.team_count = team_count
        self.team_profiles = {}
        self.position_scarcity = {"QB": 12, "RB": 24, "WR": 36, "TE": 12}  # Baseline starters
        
    def analyze_draft_patterns(self, draft_picks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze existing draft picks to understand opponent patterns."""
        team_patterns = defaultdict(lambda: {
            "positions_drafted": defaultdict(int),
            "avg_adp_deviation": 0,
            "total_picks": 0,
            "early_run_positions": [],
            "risk_tolerance": "medium"
        })
        
        for pick in draft_picks:
            team_slot = pick.get("team_slot", "unknown")
            position = pick.get("player", {}).get("position", "")
            adp = pick.get("player", {}).get("adp", 0)
            pick_number = pick.get("pick", 0)
            round_num = pick.get("round", 1)
            
            if team_slot and position:
                team_patterns[team_slot]["positions_drafted"][position] += 1
                team_patterns[team_slot]["total_picks"] += 1
                
                # Calculate ADP deviation (positive = reached, negative = fell)
                expected_pick = adp if adp > 0 else pick_number
                deviation = pick_number - expected_pick
                team_patterns[team_slot]["avg_adp_deviation"] = (
                    (team_patterns[team_slot]["avg_adp_deviation"] * (team_patterns[team_slot]["total_picks"] - 1) + deviation) /
                    team_patterns[team_slot]["total_picks"]
                )
        
        # Determine risk tolerance based on ADP deviation
        for team, pattern in team_patterns.items():
            avg_dev = pattern["avg_adp_deviation"]
            if avg_dev > 12:  # Consistently reaching for players
                pattern["risk_tolerance"] = "high"
            elif avg_dev < -12:  # Consistently taking falling players
                pattern["risk_tolerance"] = "low"
            else:
                pattern["risk_tolerance"] = "medium"
        
        self.team_profiles = dict(team_patterns)
        return self.team_profiles
    
    def predict_next_picks(self, current_pick: int, available_players: List[Dict[str, Any]], 
                          picks_until_user_turn: int = 5) -> List[Dict[str, Any]]:
        """Predict which players are likely to be taken before user's next turn."""
        
        likely_picks = []
        remaining_picks = picks_until_user_turn
        pick_probabilities = []
        
        # Calculate pick probability for each available player
        for player in available_players:
            probability = self._calculate_pick_probability(player, current_pick)
            pick_probabilities.append((player, probability))
        
        # Sort by probability descending
        pick_probabilities.sort(key=lambda x: x[1], reverse=True)
        
        # Select most likely picks
        cumulative_prob = 0.0
        for player, prob in pick_probabilities:
            if len(likely_picks) >= remaining_picks:
                break
                
            # Use probabilistic selection weighted by likelihood
            if prob > 0.3 or cumulative_prob < 0.7:  # High individual probability or need to fill quota
                likely_picks.append({
                    "player": player,
                    "probability": round(prob, 3),
                    "reasoning": self._explain_pick_probability(player, prob),
                    "urgency": "high" if prob > 0.6 else ("medium" if prob > 0.3 else "low")
                })
                cumulative_prob += prob
        
        return likely_picks
    
    def get_positional_runs(self, available_players: List[Dict[str, Any]], current_round: int) -> List[Dict[str, Any]]:
        """Identify potential positional runs that might start soon."""
        
        position_analysis = defaultdict(lambda: {
            "available_count": 0,
            "tier_1_available": 0,
            "avg_adp": 0,
            "run_likelihood": 0.0
        })
        
        # Analyze available players by position
        for player in available_players:
            pos = player.get("position", "")
            tier = player.get("tier", 999)
            adp = player.get("adp", 999)
            
            if pos:
                position_analysis[pos]["available_count"] += 1
                if tier == 1:
                    position_analysis[pos]["tier_1_available"] += 1
                if adp > 0:
                    current_adp_sum = position_analysis[pos]["avg_adp"] * (position_analysis[pos]["available_count"] - 1)
                    position_analysis[pos]["avg_adp"] = (current_adp_sum + adp) / position_analysis[pos]["available_count"]
        
        # Calculate run likelihood
        runs = []
        for pos, analysis in position_analysis.items():
            # Run likelihood factors:
            # 1. Multiple tier 1 players available
            # 2. Position scarcity (fewer total starters)
            # 3. Round appropriateness (QBs in early rounds, etc.)
            
            tier_1_factor = min(analysis["tier_1_available"] / 3, 1.0)  # Cap at 1.0
            scarcity_factor = (48 - self.position_scarcity.get(pos, 24)) / 48  # Higher scarcity = higher factor
            
            # Round appropriateness (some positions drafted earlier)
            round_factors = {
                "RB": 1.0 if current_round <= 3 else 0.7,
                "WR": 1.0 if current_round <= 4 else 0.8,
                "QB": 0.3 if current_round <= 2 else (0.8 if current_round <= 6 else 1.0),
                "TE": 0.4 if current_round <= 3 else 1.0
            }
            round_factor = round_factors.get(pos, 0.8)
            
            run_likelihood = (tier_1_factor * 0.4 + scarcity_factor * 0.3 + round_factor * 0.3)
            analysis["run_likelihood"] = run_likelihood
            
            if run_likelihood > 0.4 and analysis["available_count"] > 2:
                runs.append({
                    "position": pos,
                    "likelihood": round(run_likelihood, 3),
                    "tier_1_available": analysis["tier_1_available"],
                    "total_available": analysis["available_count"],
                    "message": f"{pos} run possible - {analysis['tier_1_available']} tier 1 players available"
                })
        
        return sorted(runs, key=lambda x: x["likelihood"], reverse=True)
    
    def _calculate_pick_probability(self, player: Dict[str, Any], current_pick: int) -> float:
        """Calculate probability that a player will be picked in the next few picks."""
        
        # Base factors
        adp = player.get("adp", 999)
        tier = player.get("tier", 999)
        position = player.get("position", "")
        vorp = player.get("vorp", 0)
        injury_status = player.get("injury_status", "Healthy")
        
        # ADP factor (most important)
        if adp > 0:
            adp_diff = current_pick - adp
            if adp_diff > 24:  # Player falling significantly
                adp_factor = 0.9  # Very likely to be picked
            elif adp_diff > 12:
                adp_factor = 0.7
            elif adp_diff > 0:
                adp_factor = 0.5  # Right around ADP
            elif adp_diff > -12:
                adp_factor = 0.3  # Slight reach
            else:
                adp_factor = 0.1  # Big reach
        else:
            adp_factor = 0.3  # Unknown ADP
        
        # Tier factor
        tier_factor = max(0, 1.0 - (tier - 1) * 0.2)  # Tier 1 = 1.0, Tier 2 = 0.8, etc.
        
        # Position scarcity factor
        scarcity_factors = {"QB": 0.3, "RB": 0.9, "WR": 0.8, "TE": 0.4}  # RBs/WRs picked more frequently
        scarcity_factor = scarcity_factors.get(position, 0.5)
        
        # VORP factor (value remaining)
        vorp_factor = min(vorp / 100, 1.0) if vorp > 0 else 0.2
        
        # Injury factor
        injury_factor = 0.7 if injury_status != "Healthy" else 1.0
        
        # Combine factors
        probability = (
            adp_factor * 0.4 +
            tier_factor * 0.2 +
            scarcity_factor * 0.2 +
            vorp_factor * 0.1 +
            injury_factor * 0.1
        )
        
        return min(max(probability, 0.0), 1.0)  # Clamp between 0 and 1
    
    def _explain_pick_probability(self, player: Dict[str, Any], probability: float) -> str:
        """Generate human-readable explanation for pick probability."""
        
        name = player.get("name", "Unknown")
        position = player.get("position", "")
        adp = player.get("adp", 0)
        tier = player.get("tier", 999)
        
        reasons = []
        
        if probability > 0.7:
            reasons.append(f"{name} very likely to go")
        elif probability > 0.4:
            reasons.append(f"{name} likely to go")
        else:
            reasons.append(f"{name} possible pick")
        
        if tier == 1:
            reasons.append("tier 1 player")
        elif tier == 2:
            reasons.append("tier 2 player")
        
        if adp > 0:
            reasons.append(f"ADP {adp:.1f}")
        
        return " - ".join(reasons)


# Legacy/simplified functions for compatibility
def predict_opponent_picks(
    opponent_roster: List[Dict[str, Any]],
    available_players: List[Dict[str, Any]],
    round_number: int
) -> List[Dict[str, Any]]:
    """
    Legacy function - predict which players an opponent is likely to draft next.
    """
    predictions = []
    
    for player in available_players[:10]:  # Top 10 available
        # Simple heuristic: higher probability for higher VORP
        probability = min(0.8, player.get("vorp", 0) / 100)
        predictions.append({
            "player": player,
            "probability": probability,
            "reason": "High VORP and positional need"
        })
    
    return sorted(predictions, key=lambda x: x["probability"], reverse=True)[:3]


def analyze_team_needs(roster: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Analyze positional needs for a team roster.
    """
    position_counts = {"QB": 0, "RB": 0, "WR": 0, "TE": 0}
    
    for player in roster:
        pos = player.get("position", "")
        if pos in position_counts:
            position_counts[pos] += 1
    
    # Calculate needs (higher number = more need)
    needs = {
        "QB": max(0, 2 - position_counts["QB"]),
        "RB": max(0, 4 - position_counts["RB"]),
        "WR": max(0, 5 - position_counts["WR"]),
        "TE": max(0, 2 - position_counts["TE"])
    }
    
    return needs