"""Draft API routes."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class DraftPickRequest(BaseModel):
    """Request model for draft pick."""
    league_id: str
    player_id: str
    team_slot: Optional[str] = None
    round: int
    pick: int


@router.post("/pick")
async def make_pick(request: DraftPickRequest):
    """Record a draft pick and update availability."""
    # TODO: Implement draft pick logic
    return {
        "success": True,
        "player_id": request.player_id,
        "message": "Draft pick endpoint - to be implemented"
    }


@router.post("/sync/sleeper")
async def sync_sleeper(league_id: str):
    """Sync with Sleeper league for live draft."""
    # TODO: Implement Sleeper sync
    return {
        "success": True,
        "league_id": league_id,
        "message": "Sleeper sync endpoint - to be implemented"
    }