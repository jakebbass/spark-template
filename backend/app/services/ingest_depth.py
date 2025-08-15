"""Depth chart ingestion service."""

import pandas as pd
from typing import List, Dict, Any


async def ingest_depth_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Ingest depth charts from CSV file.
    
    Args:
        file_path: Path to depth chart CSV file
        
    Returns:
        List of depth chart dictionaries
    """
    try:
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    except Exception as e:
        print(f"Error reading depth CSV: {e}")
        return []


async def update_depth_db(depth_data: List[Dict[str, Any]]):
    """
    Update depth charts in database.
    
    Args:
        depth_data: List of depth chart dictionaries to insert/update
    """
    from app.db.base import AsyncSessionLocal
    from app.db.models import Player, DepthChart
    from sqlalchemy import select, delete
    
    if not depth_data:
        return
    
    async with AsyncSessionLocal() as session:
        try:
            # Clear existing depth chart data
            await session.execute(delete(DepthChart))
            
            for depth_entry in depth_data:
                # Find player by sleeper_id
                player_query = select(Player).where(
                    Player.xrefs['sleeper_id'].astext == str(depth_entry.get('sleeper_id'))
                )
                result = await session.execute(player_query)
                player = result.scalar_one_or_none()
                
                if not player:
                    # Create new player if not found
                    player = Player(
                        name=depth_entry.get('player_name'),
                        team=depth_entry.get('team'),
                        position=depth_entry.get('position'),
                        xrefs={'sleeper_id': str(depth_entry.get('sleeper_id'))}
                    )
                    session.add(player)
                    await session.flush()  # Get the ID
                
                # Insert depth chart entry
                depth_chart = DepthChart(
                    team=depth_entry.get('team'),
                    position=depth_entry.get('position'),
                    player_id=player.id,
                    rank=depth_entry.get('rank', 1)
                )
                session.add(depth_chart)
            
            await session.commit()
            print(f"Successfully updated {len(depth_data)} depth chart entries")
            
        except Exception as e:
            await session.rollback()
            print(f"Error updating depth chart: {e}")
            raise