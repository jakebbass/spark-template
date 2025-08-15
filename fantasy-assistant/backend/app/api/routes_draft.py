"""Draft API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import redis

from app.db.base import get_db
from app.db.models import Player, DraftPick
from app.core.config import settings

router = APIRouter()


class DraftPickRequest(BaseModel):
    """Request model for draft pick."""
    league_id: str
    player_id: str
    team_slot: Optional[str] = None
    round: int
    pick: int


@router.post("/pick")
async def make_pick(request: DraftPickRequest, db: AsyncSession = Depends(get_db)):
    """Record a draft pick and update availability."""
    try:
        # Verify player exists
        player_query = select(Player).where(Player.id == request.player_id)
        result = await db.execute(player_query)
        player = result.scalar_one_or_none()
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Check if player is already drafted in this league
        existing_pick_query = select(DraftPick).where(
            (DraftPick.league_id == request.league_id) &
            (DraftPick.player_id == request.player_id)
        )
        result = await db.execute(existing_pick_query)
        existing_pick = result.scalar_one_or_none()
        
        if existing_pick:
            raise HTTPException(status_code=400, detail="Player already drafted in this league")
        
        # Record the draft pick
        draft_pick = DraftPick(
            league_id=request.league_id,
            player_id=request.player_id,
            team_slot=request.team_slot,
            round=request.round,
            pick=request.pick
        )
        
        db.add(draft_pick)
        await db.commit()
        
        # Update Redis cache to mark player as taken
        try:
            redis_client = redis.from_url(settings.redis_url)
            taken_key = f"league:{request.league_id}:taken"
            redis_client.sadd(taken_key, request.player_id)
        except Exception as redis_error:
            print(f"Redis cache update failed: {redis_error}")
            # Continue without cache update
        
        return {
            "success": True,
            "player_id": request.player_id,
            "player_name": player.name,
            "league_id": request.league_id,
            "round": request.round,
            "pick": request.pick,
            "message": f"Successfully drafted {player.name} (Round {request.round}, Pick {request.pick})"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording draft pick: {str(e)}")


@router.get("/picks/{league_id}")
async def get_draft_picks(league_id: str, db: AsyncSession = Depends(get_db)):
    """Get all draft picks for a league."""
    try:
        query = select(DraftPick, Player).join(Player).where(
            DraftPick.league_id == league_id
        ).order_by(DraftPick.round, DraftPick.pick)
        
        result = await db.execute(query)
        picks = result.all()
        
        draft_board = []
        for draft_pick, player in picks:
            draft_board.append({
                "id": str(draft_pick.id),
                "round": draft_pick.round,
                "pick": draft_pick.pick,
                "team_slot": draft_pick.team_slot,
                "player": {
                    "id": str(player.id),
                    "name": player.name,
                    "team": player.team,
                    "position": player.position
                },
                "timestamp": draft_pick.ts.isoformat() if draft_pick.ts else None
            })
        
        return {
            "league_id": league_id,
            "picks": draft_board,
            "total_picks": len(draft_board)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching draft picks: {str(e)}")


@router.delete("/pick/{league_id}/{player_id}")
async def undo_pick(league_id: str, player_id: str, db: AsyncSession = Depends(get_db)):
    """Undo a draft pick (remove from draft board)."""
    try:
        # Find the draft pick
        query = select(DraftPick).where(
            (DraftPick.league_id == league_id) &
            (DraftPick.player_id == player_id)
        )
        result = await db.execute(query)
        draft_pick = result.scalar_one_or_none()
        
        if not draft_pick:
            raise HTTPException(status_code=404, detail="Draft pick not found")
        
        # Remove from database
        await db.delete(draft_pick)
        await db.commit()
        
        # Update Redis cache
        try:
            redis_client = redis.from_url(settings.redis_url)
            taken_key = f"league:{league_id}:taken"
            redis_client.srem(taken_key, player_id)
        except Exception as redis_error:
            print(f"Redis cache update failed: {redis_error}")
        
        return {
            "success": True,
            "message": "Draft pick successfully removed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error undoing draft pick: {str(e)}")


@router.post("/sync/sleeper")
async def sync_sleeper(league_id: str, db: AsyncSession = Depends(get_db)):
    """Sync with Sleeper league for live draft."""
    # TODO: Implement actual Sleeper API integration
    # For now, return a placeholder response
    
    if not settings.sleeper_league_id:
        return {
            "success": False,
            "error": "No Sleeper league ID configured",
            "message": "Sleeper sync not available - configure SLEEPER_LEAGUE_ID"
        }
    
    # Placeholder for Sleeper API integration
    return {
        "success": True,
        "league_id": league_id,
        "sleeper_league_id": settings.sleeper_league_id,
        "message": "Sleeper sync endpoint - implementation pending",
        "note": "This would fetch live draft data from Sleeper API when implemented"
    }