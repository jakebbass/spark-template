"""Tests for draft advice functionality."""

import pytest
from unittest.mock import Mock
from app.core.opponent_model import predict_opponent_picks, analyze_team_needs


class TestAdvice:
    """Test draft advice functionality."""
    
    def test_analyze_team_needs_basic(self):
        """Test team needs analysis."""
        roster = [
            {"name": "QB1", "position": "QB"},
            {"name": "RB1", "position": "RB"},
            {"name": "WR1", "position": "WR"},
            {"name": "WR2", "position": "WR"}
        ]
        
        needs = analyze_team_needs(roster)
        
        assert needs["QB"] == 1  # Need 1 more QB (2 total desired - 1 current)
        assert needs["RB"] == 3  # Need 3 more RB (4 total desired - 1 current)
        assert needs["WR"] == 3  # Need 3 more WR (5 total desired - 2 current)
        assert needs["TE"] == 2  # Need 2 more TE (2 total desired - 0 current)
    
    def test_analyze_team_needs_full_roster(self):
        """Test needs analysis with full roster."""
        roster = [
            {"name": "QB1", "position": "QB"},
            {"name": "QB2", "position": "QB"},
            {"name": "RB1", "position": "RB"},
            {"name": "RB2", "position": "RB"},
            {"name": "RB3", "position": "RB"},
            {"name": "RB4", "position": "RB"},
            {"name": "WR1", "position": "WR"},
            {"name": "WR2", "position": "WR"},
            {"name": "WR3", "position": "WR"},
            {"name": "WR4", "position": "WR"},
            {"name": "WR5", "position": "WR"},
            {"name": "TE1", "position": "TE"},
            {"name": "TE2", "position": "TE"}
        ]
        
        needs = analyze_team_needs(roster)
        
        # All positions filled, no needs
        assert needs["QB"] == 0
        assert needs["RB"] == 0
        assert needs["WR"] == 0
        assert needs["TE"] == 0
    
    def test_predict_opponent_picks_basic(self):
        """Test opponent pick prediction."""
        opponent_roster = [
            {"name": "QB1", "position": "QB"}
        ]
        
        available_players = [
            {"name": "RB1", "position": "RB", "vorp": 50},
            {"name": "WR1", "position": "WR", "vorp": 40},
            {"name": "TE1", "position": "TE", "vorp": 20}
        ]
        
        predictions = predict_opponent_picks(opponent_roster, available_players, 2)
        
        # Should return predictions
        assert len(predictions) <= 3
        assert all("player" in p for p in predictions)
        assert all("probability" in p for p in predictions)
        assert all("reason" in p for p in predictions)
    
    def test_predict_opponent_picks_empty_available(self):
        """Test prediction with no available players."""
        opponent_roster = [{"name": "QB1", "position": "QB"}]
        available_players = []
        
        predictions = predict_opponent_picks(opponent_roster, available_players, 2)
        
        assert predictions == []