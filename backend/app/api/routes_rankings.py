"""Rankings API routes."""

from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()


@router.get("/")
async def get_rankings(
    pos: Optional[str] = Query(None, description="Position filter (QB, RB, WR, TE)"),
    limit: int = Query(250, description="Number of players to return"),
    scoring_profile: Optional[str] = Query(None, description="Custom scoring profile"),
):
    """Get player rankings with projections, VORP, tiers, and advanced metrics."""
    # TODO: Implement rankings logic
    return {
        "players": [],
        "total": 0,
        "message": "Rankings endpoint - to be implemented"
    }