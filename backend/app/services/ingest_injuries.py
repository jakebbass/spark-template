"""Injury data ingestion service."""

import pandas as pd
from typing import List, Dict, Any
import httpx
from app.core.config import settings


async def ingest_injuries_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Ingest injury data from CSV file (fallback when no API key).
    
    Args:
        file_path: Path to injuries CSV file
        
    Returns:
        List of injury dictionaries
    """
    try:
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    except Exception as e:
        print(f"Error reading injuries CSV: {e}")
        return []


async def ingest_injuries_api() -> List[Dict[str, Any]]:
    """
    Ingest injury data from external API.
    
    Returns:
        List of injury dictionaries
    """
    if not settings.injuries_api_key:
        print("No injuries API key found, using CSV fallback")
        return await ingest_injuries_csv("data/injuries.csv")
    
    # TODO: Implement real API integration
    async with httpx.AsyncClient() as client:
        # Placeholder API call
        # response = await client.get("https://api.example.com/injuries")
        pass
    
    return []


async def update_injuries_db(injuries: List[Dict[str, Any]]):
    """
    Update injury data in database.
    
    Args:
        injuries: List of injury dictionaries to insert/update
    """
    from app.db.base import AsyncSessionLocal
    from app.db.models import Player, Injury
    from sqlalchemy import select
    from sqlalchemy.dialects.postgresql import insert
    
    if not injuries:
        return
    
    async with AsyncSessionLocal() as session:
        try:
            for injury_data in injuries:
                # Find player by sleeper_id
                player_query = select(Player).where(
                    Player.xrefs['sleeper_id'].astext == str(injury_data.get('sleeper_id'))
                )
                result = await session.execute(player_query)
                player = result.scalar_one_or_none()
                
                if not player:
                    # Create new player if not found
                    player = Player(
                        name=injury_data.get('player_name'),
                        team=injury_data.get('team'),
                        position=injury_data.get('position'),
                        xrefs={'sleeper_id': str(injury_data.get('sleeper_id'))}
                    )
                    session.add(player)
                    await session.flush()  # Get the ID
                
                # Upsert injury
                injury_insert = insert(Injury).values(
                    player_id=player.id,
                    status=injury_data.get('status', 'Healthy'),
                    note=injury_data.get('note', '')
                )
                injury_upsert = injury_insert.on_conflict_do_update(
                    index_elements=['player_id'],
                    set_=dict(
                        status=injury_insert.excluded.status,
                        note=injury_insert.excluded.note,
                        updated_at=injury_insert.excluded.updated_at
                    )
                )
                await session.execute(injury_upsert)
            
            await session.commit()
            print(f"Successfully updated {len(injuries)} injury records")
            
        except Exception as e:
            await session.rollback()
            print(f"Error updating injuries: {e}")
            raise