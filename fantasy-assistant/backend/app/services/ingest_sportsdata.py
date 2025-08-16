"""Ingest data from sportsdata.io with async httpx, Redis caching and DB upserts."""
from __future__ import annotations

import os
import asyncio
from typing import Any, Dict, List, Optional

import httpx
from redis import asyncio as aioredis

from app.db.base import AsyncSessionLocal
from app.db.models import Player, Projection, Injury
from sqlalchemy import select


SPORTS_KEY = os.getenv("PROJECTIONS_API_KEY") or os.getenv("SPORTS_DATA_API_KEY")
BASE_URL = "https://api.sportsdata.io/v3/nfl"


async def _get_redis() -> aioredis.Redis:
    url = os.getenv("REDIS_URL", "redis://cache:6379/0")
    return aioredis.from_url(url)


def _headers() -> Dict[str, str]:
    if not SPORTS_KEY:
        return {}
    return {"Ocp-Apim-Subscription-Key": SPORTS_KEY}


async def fetch_players(season: int) -> List[Dict[str, Any]]:
    """Fetch players list (cached in Redis)."""
    cache_key = f"sportsdata:players:{season}"
    redis = await _get_redis()
    cached = await redis.get(cache_key)
    if cached:
        try:
            import orjson
            return orjson.loads(cached)
        except Exception:
            pass

    url = f"{BASE_URL}/scores/json/Players"
    params = {"season": season}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params, headers=_headers())
        resp.raise_for_status()
        data = resp.json()

    # cache for 6 hours
    await redis.set(cache_key, orjson.dumps(data), ex=60 * 60 * 6)
    return data


async def fetch_projections(season: int) -> List[Dict[str, Any]]:
    """Fetch season projections (cached)."""
    cache_key = f"sportsdata:projections:{season}"
    redis = await _get_redis()
    cached = await redis.get(cache_key)
    if cached:
        try:
            import orjson
            return orjson.loads(cached)
        except Exception:
            pass

    url = f"{BASE_URL}/stats/json/PlayerSeasonStats/{season}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(url, headers=_headers())
        resp.raise_for_status()
        data = resp.json()

    await redis.set(cache_key, orjson.dumps(data), ex=60 * 60 * 6)
    return data


async def fetch_injuries(season: int) -> List[Dict[str, Any]]:
    cache_key = f"sportsdata:injuries:{season}"
    redis = await _get_redis()
    cached = await redis.get(cache_key)
    if cached:
        try:
            import orjson
            return orjson.loads(cached)
        except Exception:
            pass

    url = f"{BASE_URL}/scores/json/Injuries/{season}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, headers=_headers())
        resp.raise_for_status()
        data = resp.json()

    await redis.set(cache_key, orjson.dumps(data), ex=60 * 30)
    return data


async def upsert_players(players: List[Dict[str, Any]]):
    """Upsert players into DB (simple name/team matching)."""
    async with AsyncSessionLocal() as session:
        for p in players:
            name = p.get("Name") or p.get("name")
            team = p.get("Team") or p.get("team") or ""
            position = p.get("Position") or p.get("position") or ""
            if not name or not team:
                continue
            stmt = select(Player).where(Player.name.ilike(name), Player.team == team)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                # update basic fields
                existing.position = position or existing.position
            else:
                new = Player(name=name, team=team, position=position)
                session.add(new)
        await session.commit()


async def upsert_projections(projs: List[Dict[str, Any]], season: int, source: str = "sportsdata"):
    async with AsyncSessionLocal() as session:
        for p in projs:
            player_name = p.get("Name") or p.get("name")
            # find player
            stmt = select(Player).where(Player.name.ilike(player_name))
            result = await session.execute(stmt)
            player = result.scalar_one_or_none()
            if not player:
                continue
            proj = Projection(player_id=player.id, season=season, source=source, stats=p)
            session.add(proj)
        await session.commit()


async def upsert_injuries(injs: List[Dict[str, Any]], season: int):
    async with AsyncSessionLocal() as session:
        for inj in injs:
            player_name = inj.get("Name") or inj.get("name")
            status = inj.get("Status") or inj.get("status") or "Unknown"
            stmt = select(Player).where(Player.name.ilike(player_name))
            result = await session.execute(stmt)
            player = result.scalar_one_or_none()
            if not player:
                continue
            record = Injury(player_id=player.id, status=status, note=inj.get("Notes") or "")
            session.add(record)
        await session.commit()


async def run_season_ingest(season: int = 2024):
    if not SPORTS_KEY:
        raise RuntimeError("SPORTS DATA API key not set in environment (PROJECTIONS_API_KEY or SPORTS_DATA_API_KEY)")

    players = await fetch_players(season)
    await upsert_players(players)

    projs = await fetch_projections(season)
    await upsert_projections(projs, season)

    injs = await fetch_injuries(season)
    await upsert_injuries(injs, season)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, default=2024)
    args = parser.parse_args()
    asyncio.run(run_season_ingest(args.season))
