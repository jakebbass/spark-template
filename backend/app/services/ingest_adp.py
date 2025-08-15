"""ADP (Average Draft Position) ingestion service."""

import pandas as pd
from typing import List, Dict, Any


async def ingest_adp_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Ingest ADP data from CSV file (fallback when no API key).
    
    Args:
        file_path: Path to ADP CSV file
        
    Returns:
        List of ADP dictionaries
    """
    try:
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    except Exception as e:
        print(f"Error reading ADP CSV: {e}")
        return []


async def update_adp_db(adp_data: List[Dict[str, Any]]):
    """
    Update ADP data in database.
    
    Args:
        adp_data: List of ADP dictionaries to insert/update
    """
    from app.db.base import AsyncSessionLocal
    from app.db.models import Player, ADP
    from sqlalchemy import select
    from sqlalchemy.dialects.postgresql import insert
    
    if not adp_data:
        return
    
    async with AsyncSessionLocal() as session:
        try:
            for adp_entry in adp_data:
                # Find player by sleeper_id
                player_query = select(Player).where(
                    Player.xrefs['sleeper_id'].astext == str(adp_entry.get('sleeper_id'))
                )
                result = await session.execute(player_query)
                player = result.scalar_one_or_none()
                
                if not player:
                    # Create new player if not found
                    player = Player(
                        name=adp_entry.get('player_name'),
                        team=adp_entry.get('team'),
                        position=adp_entry.get('position'),
                        xrefs={'sleeper_id': str(adp_entry.get('sleeper_id'))}
                    )
                    session.add(player)
                    await session.flush()  # Get the ID
                
                # Upsert ADP
                adp_insert = insert(ADP).values(
                    player_id=player.id,
                    platform=adp_entry.get('platform', 'sleeper'),
                    adp=float(adp_entry.get('adp', 0)),
                    sample_size=int(adp_entry.get('sample_size', 0))
                )
                adp_upsert = adp_insert.on_conflict_do_update(
                    index_elements=['player_id', 'platform'],
                    set_=dict(
                        adp=adp_insert.excluded.adp,
                        sample_size=adp_insert.excluded.sample_size,
                        updated_at=adp_insert.excluded.updated_at
                    )
                )
                await session.execute(adp_upsert)
            
            await session.commit()
            print(f"Successfully updated {len(adp_data)} ADP records")
            
        except Exception as e:
            await session.rollback()
            print(f"Error updating ADP: {e}")
            raise