"""Draft advice API routes."""

from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()


@router.get("/")
async def get_advice(
    league_id: str = Query(..., description="League identifier"),
    round: int = Query(..., description="Current draft round"),
    pick: int = Query(..., description="Current pick number"),
    roster_state: Optional[str] = Query(None, description="JSON string of current roster"),
):
    """Get draft advice including top recommendations and rationale."""
    # TODO: Implement advice logic
    return {
        "top5": [],
        "rationale": "Draft advice endpoint - to be implemented",
        "fallbacks": [],
        "exposure_warnings": [],
        "opponent_predictions": []
    }