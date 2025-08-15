"""Tests for Monte Carlo simulations."""

import pytest
from app.core.monte_carlo import simulate_season, batch_simulate_players


class TestMonteCarlo:
    """Test Monte Carlo simulation functionality."""
    
    def test_simulate_season_basic(self):
        """Test basic season simulation."""
        player_stats = {
            "name": "Test Player",
            "fantasy_points": 200
        }
        
        result = simulate_season(player_stats, n_simulations=100)
        
        # Check that all required keys are present
        assert "p10" in result
        assert "p50" in result
        assert "p90" in result
        assert "volatility" in result
        assert "boom_bust_ratio" in result
        
        # p50 should be close to projected points
        assert result["p50"] == 200
        
        # p10 should be less than p50, p90 should be greater
        assert result["p10"] <= result["p50"]
        assert result["p50"] <= result["p90"]
    
    def test_simulate_season_zero_points(self):
        """Test simulation with zero projected points."""
        player_stats = {
            "name": "Bench Player",
            "fantasy_points": 0
        }
        
        result = simulate_season(player_stats)
        
        assert result["p50"] == 0
        assert result["p10"] <= result["p90"]
    
    def test_batch_simulate_players(self):
        """Test batch simulation of multiple players."""
        players = [
            {"name": "Player1", "fantasy_points": 200},
            {"name": "Player2", "fantasy_points": 150},
            {"name": "Player3", "fantasy_points": 100}
        ]
        
        result = batch_simulate_players(players)
        
        # Should return same number of players
        assert len(result) == 3
        
        # Each player should have Monte Carlo metrics
        for player in result:
            assert "p10" in player
            assert "p50" in player
            assert "p90" in player
            assert "volatility" in player
    
    def test_batch_simulate_empty_list(self):
        """Test batch simulation with empty list."""
        result = batch_simulate_players([])
        assert result == []