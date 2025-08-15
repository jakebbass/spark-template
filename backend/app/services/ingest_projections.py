"""Projection data ingestion service."""

import pandas as pd
from typing import List, Dict, Any
import httpx
from app.core.config import settings


async def ingest_projections_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Ingest projections from CSV file (fallback when no API key).
    
    Args:
        file_path: Path to projections CSV file
        
    Returns:
        List of projection dictionaries
    """
    try:
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    except Exception as e:
        print(f"Error reading projections CSV: {e}")
        return []


async def ingest_projections_api() -> List[Dict[str, Any]]:
    """
    Ingest projections from external API.
    
    Returns:
        List of projection dictionaries
    """
    if not settings.projections_api_key:
        print("No projections API key found, using CSV fallback")
        return await ingest_projections_csv("data/projections.csv")
    
    # TODO: Implement real API integration
    async with httpx.AsyncClient() as client:
        # Placeholder API call
        # response = await client.get("https://api.example.com/projections")
        pass
    
    return []


async def update_projections_db(projections: List[Dict[str, Any]]):
    """
    Update projections in database.
    
    Args:
        projections: List of projection dictionaries to insert/update
    """
    from app.db.base import AsyncSessionLocal
    from app.db.models import Player, Projection
    from sqlalchemy import select
    from sqlalchemy.dialects.postgresql import insert
    
    if not projections:
        return
    
    async with AsyncSessionLocal() as session:
        try:
            current_season = 2024
            
            for proj_data in projections:
                # Find player by sleeper_id
                player_query = select(Player).where(
                    Player.xrefs['sleeper_id'].astext == str(proj_data.get('sleeper_id'))
                )
                result = await session.execute(player_query)
                player = result.scalar_one_or_none()
                
                if not player:
                    # Create new player if not found
                    player = Player(
                        name=proj_data.get('player_name'),
                        team=proj_data.get('team'),
                        position=proj_data.get('position'),
                        xrefs={'sleeper_id': str(proj_data.get('sleeper_id'))}
                    )
                    session.add(player)
                    await session.flush()  # Get the ID
                
                # Prepare stats dict (exclude non-stat columns)
                stats = {k: v for k, v in proj_data.items() 
                        if k not in ['player_name', 'team', 'position', 'sleeper_id']}
                
                # Upsert projection
                projection_insert = insert(Projection).values(
                    player_id=player.id,
                    season=current_season,
                    source='csv_fallback',
                    stats=stats
                )
                projection_upsert = projection_insert.on_conflict_do_update(
                    index_elements=['player_id', 'season', 'source'],
                    set_=dict(
                        stats=projection_insert.excluded.stats,
                        updated_at=projection_insert.excluded.updated_at
                    )
                )
                await session.execute(projection_upsert)
            
            await session.commit()
            print(f"Successfully updated {len(projections)} projections")
            
        except Exception as e:
            await session.rollback()
            print(f"Error updating projections: {e}")
            raise