"""Sleeper platform integration service."""

import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings


class SleeperClient:
    """Client for Sleeper API integration."""
    
    BASE_URL = "https://api.sleeper.app/v1"
    
    async def get_league(self, league_id: str) -> Optional[Dict[str, Any]]:
        """Get league information from Sleeper."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.BASE_URL}/league/{league_id}")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching Sleeper league: {e}")
                return None
    
    async def get_league_drafts(self, league_id: str) -> List[Dict[str, Any]]:
        """Get draft information for a league."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.BASE_URL}/league/{league_id}/drafts")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching Sleeper drafts: {e}")
                return []
    
    async def get_draft_picks(self, draft_id: str) -> List[Dict[str, Any]]:
        """Get picks for a specific draft."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.BASE_URL}/draft/{draft_id}/picks")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching Sleeper picks: {e}")
                return []
    
    async def get_players(self) -> Dict[str, Any]:
        """Get all NFL players from Sleeper."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.BASE_URL}/players/nfl")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching Sleeper players: {e}")
                return {}


async def sync_sleeper_league(league_id: str) -> Dict[str, Any]:
    """
    Sync a Sleeper league and return draft data.
    
    Args:
        league_id: Sleeper league ID
        
    Returns:
        Dictionary with league and draft information
    """
    client = SleeperClient()
    
    # Get league info
    league = await client.get_league(league_id)
    if not league:
        return {"error": "League not found"}
    
    # Get draft info
    drafts = await client.get_league_drafts(league_id)
    if not drafts:
        return {"error": "No drafts found"}
    
    # Get picks for the most recent draft
    draft_id = drafts[0]["draft_id"]
    picks = await client.get_draft_picks(draft_id)
    
    return {
        "league": league,
        "draft": drafts[0],
        "picks": picks
    }