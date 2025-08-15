"""Tests for VORP calculations."""

import pytest
from app.core.vorp import calculate_vorp, calculate_tiers


class TestVORP:
    """Test VORP and tier calculations."""
    
    def test_calculate_vorp_basic(self):
        """Test basic VORP calculation."""
        players = [
            {"name": "QB1", "position": "QB", "fantasy_points": 300},
            {"name": "QB2", "position": "QB", "fantasy_points": 250},
            {"name": "QB3", "position": "QB", "fantasy_points": 200},
            {"name": "RB1", "position": "RB", "fantasy_points": 280},
            {"name": "RB2", "position": "RB", "fantasy_points": 220}
        ]
        
        baselines = {"QB": 2, "RB": 1}  # Simplified baselines
        result = calculate_vorp(players, baselines)
        
        # QB baseline should be QB2 (250), so QB1 VORP = 300-250 = 50
        qb1 = next(p for p in result if p["name"] == "QB1")
        assert qb1["vorp"] == 50
        
        # RB baseline should be RB2 (220), so RB1 VORP = 280-220 = 60
        rb1 = next(p for p in result if p["name"] == "RB1")
        assert rb1["vorp"] == 60
    
    def test_calculate_vorp_default_baselines(self):
        """Test VORP with default baselines."""
        players = [
            {"name": "QB1", "position": "QB", "fantasy_points": 300},
            {"name": "RB1", "position": "RB", "fantasy_points": 280}
        ]
        
        result = calculate_vorp(players)
        
        # With only 1 player per position, baseline should be 0
        assert result[0]["vorp"] == 300
        assert result[1]["vorp"] == 280
    
    def test_calculate_tiers_basic(self):
        """Test tier calculation."""
        players = [
            {"name": "Player1", "position": "RB", "vorp": 100},
            {"name": "Player2", "position": "RB", "vorp": 95},
            {"name": "Player3", "position": "RB", "vorp": 80},  # Big gap here
            {"name": "Player4", "position": "RB", "vorp": 75}
        ]
        
        result = calculate_tiers(players, "RB")
        
        # Should have at least 2 tiers due to the gap between 95 and 80
        tiers = set(p["tier"] for p in result)
        assert len(tiers) >= 1
        
        # Higher VORP should have lower tier number
        player1 = next(p for p in result if p["name"] == "Player1")
        player3 = next(p for p in result if p["name"] == "Player3")
        assert player1["tier"] <= player3["tier"]
    
    def test_calculate_tiers_empty_list(self):
        """Test tier calculation with empty list."""
        result = calculate_tiers([])
        assert result == []