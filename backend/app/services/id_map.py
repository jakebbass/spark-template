"""Player ID mapping across different platforms."""

import csv
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.models import Player
from app.db.base import AsyncSessionLocal

logger = logging.getLogger(__name__)


class IDMapper:
    """Map player IDs across different fantasy platforms."""
    
    def __init__(self):
        """Initialize the ID mapper with cross-reference data."""
        self.name_to_xrefs: Dict[Tuple[str, str], Dict[str, str]] = {}
        self.platform_id_to_internal: Dict[str, str] = {}
        self._load_id_mappings()
    
    def _load_id_mappings(self):
        """Load ID mappings from CSV files."""
        # Look for ID mapping CSV files in the backend data directory
        data_dir = Path(__file__).parent.parent / "data"
        id_mapping_file = data_dir / "player_id_mappings.csv"
        
        if not id_mapping_file.exists():
            logger.warning(f"ID mapping file not found at {id_mapping_file}")
            return
            
        try:
            with open(id_mapping_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get('name', '').strip()
                    team = row.get('team', '').strip()
                    
                    if not name or not team:
                        continue
                        
                    key = (name.lower(), team.upper())
                    xrefs = {}
                    
                    # Extract all ID columns
                    for platform in ['sleeper_id', 'gsis_id', 'espn_id', 'yahoo_id', 'pfr_id']:
                        if row.get(platform):
                            xrefs[platform] = row[platform].strip()
                            # Map platform ID back to name/team for reverse lookups
                            self.platform_id_to_internal[f"{platform}:{row[platform].strip()}"] = key
                    
                    if xrefs:
                        self.name_to_xrefs[key] = xrefs
                        
            logger.info(f"Loaded {len(self.name_to_xrefs)} player ID mappings")
        except Exception as e:
            logger.error(f"Failed to load ID mappings: {e}")
    
    def get_sleeper_id(self, player_name: str, team: str) -> Optional[str]:
        """Get Sleeper ID for a player."""
        key = (player_name.lower(), team.upper())
        xrefs = self.name_to_xrefs.get(key, {})
        return xrefs.get('sleeper_id')
    
    def get_gsis_id(self, player_name: str, team: str) -> Optional[str]:
        """Get NFL GSIS ID for a player."""
        key = (player_name.lower(), team.upper())
        xrefs = self.name_to_xrefs.get(key, {})
        return xrefs.get('gsis_id')
    
    def get_espn_id(self, player_name: str, team: str) -> Optional[str]:
        """Get ESPN ID for a player."""
        key = (player_name.lower(), team.upper())
        xrefs = self.name_to_xrefs.get(key, {})
        return xrefs.get('espn_id')
    
    def get_yahoo_id(self, player_name: str, team: str) -> Optional[str]:
        """Get Yahoo ID for a player."""
        key = (player_name.lower(), team.upper())
        xrefs = self.name_to_xrefs.get(key, {})
        return xrefs.get('yahoo_id')
    
    def get_pfr_id(self, player_name: str, team: str) -> Optional[str]:
        """Get Pro Football Reference ID for a player."""
        key = (player_name.lower(), team.upper())
        xrefs = self.name_to_xrefs.get(key, {})
        return xrefs.get('pfr_id')
    
    def get_all_xrefs(self, player_name: str, team: str) -> Dict[str, str]:
        """Get all cross-reference IDs for a player."""
        key = (player_name.lower(), team.upper())
        return self.name_to_xrefs.get(key, {}).copy()
    
    def normalize_player_id(self, external_id: str, platform: str) -> Optional[Tuple[str, str]]:
        """Convert external ID to player name/team tuple."""
        lookup_key = f"{platform}:{external_id}"
        name_team_key = self.platform_id_to_internal.get(lookup_key)
        
        if name_team_key:
            name, team = name_team_key
            # Return properly cased name and team
            return (name.title(), team.upper())
        
        return None
    
    async def find_player_by_external_id(self, external_id: str, platform: str) -> Optional[Player]:
        """Find a player in the database by external ID."""
        normalized = self.normalize_player_id(external_id, platform)
        if not normalized:
            return None
            
        name, team = normalized
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Player).where(
                    Player.name.ilike(name),
                    Player.team == team
                )
            )
            return result.scalar_one_or_none()
    
    async def update_player_xrefs(self, player_id: UUID, xrefs: Dict[str, str]):
        """Update cross-reference IDs for a player in the database."""
        async with AsyncSessionLocal() as session:
            try:
                await session.execute(
                    update(Player)
                    .where(Player.id == player_id)
                    .values(xrefs=xrefs)
                )
                await session.commit()
                logger.info(f"Updated xrefs for player {player_id}: {xrefs}")
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update xrefs for player {player_id}: {e}")
                raise
    
    async def bulk_update_xrefs_from_mappings(self):
        """Bulk update all player xrefs from the loaded mappings."""
        async with AsyncSessionLocal() as session:
            try:
                # Get all players
                result = await session.execute(select(Player))
                players = result.scalars().all()
                
                updated_count = 0
                for player in players:
                    xrefs = self.get_all_xrefs(player.name, player.team)
                    if xrefs and xrefs != player.xrefs:
                        player.xrefs = xrefs
                        updated_count += 1
                
                if updated_count > 0:
                    await session.commit()
                    logger.info(f"Updated xrefs for {updated_count} players")
                else:
                    logger.info("No player xrefs needed updating")
                    
                return updated_count
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to bulk update xrefs: {e}")
                raise


# Global instance
id_mapper = IDMapper()