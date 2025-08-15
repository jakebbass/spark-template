"""Tests for scoring calculations."""

import pytest
from app.core.scoring import calculate_fantasy_points, get_default_scoring


class TestScoring:
    """Test fantasy scoring calculations."""
    
    def test_calculate_fantasy_points_basic(self):
        """Test basic fantasy point calculation."""
        stats = {
            "pass_yd": 300,
            "pass_td": 2,
            "rush_yd": 50,
            "rec": 6,
            "rec_yd": 80,
            "rec_td": 1
        }
        
        # PPR scoring
        scoring_config = '{"pass_yd":0.04,"pass_td":4,"rush_yd":0.1,"rec":1,"rec_yd":0.1,"rec_td":6}'
        
        points = calculate_fantasy_points(stats, scoring_config)
        expected = (300 * 0.04) + (2 * 4) + (50 * 0.1) + (6 * 1) + (80 * 0.1) + (1 * 6)
        
        assert points == expected
    
    def test_calculate_fantasy_points_negative(self):
        """Test fantasy points with negative stats."""
        stats = {
            "pass_td": 1,
            "int": 2,
            "fumble": 1
        }
        
        scoring_config = '{"pass_td":4,"int":-2,"fumble":-2}'
        
        points = calculate_fantasy_points(stats, scoring_config)
        expected = (1 * 4) + (2 * -2) + (1 * -2)
        
        assert points == expected
    
    def test_get_default_scoring(self):
        """Test default scoring configuration."""
        scoring = get_default_scoring()
        
        assert scoring["pass_td"] == 4
        assert scoring["rec"] == 1  # PPR
        assert scoring["int"] == -2
        assert scoring["fumble"] == -2
    
    def test_missing_stats(self):
        """Test calculation with missing stats."""
        stats = {
            "pass_yd": 200,
            "pass_td": 1
        }
        
        scoring_config = '{"pass_yd":0.04,"pass_td":4,"rush_yd":0.1}'
        
        points = calculate_fantasy_points(stats, scoring_config)
        expected = (200 * 0.04) + (1 * 4)  # rush_yd not in stats, so 0
        
        assert points == expected