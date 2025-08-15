"""Historical stats ingestion service."""

import pandas as pd
from typing import List, Dict, Any


async def ingest_stats_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Ingest historical stats from CSV file.
    
    Args:
        file_path: Path to stats CSV file
        
    Returns:
        List of historical stat dictionaries
    """
    try:
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    except Exception as e:
        print(f"Error reading stats CSV: {e}")
        return []


async def update_stats_db(stats: List[Dict[str, Any]]):
    """
    Update historical stats in database.
    
    Args:
        stats: List of stat dictionaries to insert/update
    """
    from app.db.base import AsyncSessionLocal
    from app.db.models import Player, HistoricalStats
    from sqlalchemy import select
    from sqlalchemy.dialects.postgresql import insert
    
    if not stats:
        return
    
    async with AsyncSessionLocal() as session:
        try:
            for stat_data in stats:
                # Find player by sleeper_id
                player_query = select(Player).where(
                    Player.xrefs['sleeper_id'].astext == str(stat_data.get('sleeper_id'))
                )
                result = await session.execute(player_query)
                player = result.scalar_one_or_none()
                
                if not player:
                    # Create new player if not found
                    player = Player(
                        name=stat_data.get('player_name'),
                        team=stat_data.get('team'),
                        position=stat_data.get('position'),
                        xrefs={'sleeper_id': str(stat_data.get('sleeper_id'))}
                    )
                    session.add(player)
                    await session.flush()  # Get the ID
                
                season = stat_data.get('season', 2023)
                
                # Prepare stats dict (exclude non-stat columns)
                stats_dict = {k: v for k, v in stat_data.items() 
                             if k not in ['player_name', 'team', 'position', 'sleeper_id', 'season']}
                
                # Upsert historical stats
                stats_insert = insert(HistoricalStats).values(
                    player_id=player.id,
                    season=season,
                    stats=stats_dict
                )
                stats_upsert = stats_insert.on_conflict_do_update(
                    index_elements=['player_id', 'season'],
                    set_=dict(
                        stats=stats_insert.excluded.stats,
                        updated_at=stats_insert.excluded.updated_at
                    )
                )
                await session.execute(stats_upsert)
            
            await session.commit()
            print(f"Successfully updated {len(stats)} historical stats")
            
        except Exception as e:
            await session.rollback()
            print(f"Error updating historical stats: {e}")
            raise