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
    # TODO: Implement database updates
    pass