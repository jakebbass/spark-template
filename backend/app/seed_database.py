"""Master seed script to populate database with sample data."""

import asyncio
import os
from pathlib import Path

from app.services.ingest_projections import ingest_projections_csv, update_projections_db
from app.services.ingest_stats_last_year import ingest_stats_csv, update_stats_db
from app.services.ingest_injuries import ingest_injuries_csv, update_injuries_db
from app.services.ingest_depth import ingest_depth_csv, update_depth_db
from app.services.ingest_adp import ingest_adp_csv, update_adp_db


async def seed_database():
    """Run all seed jobs to populate database with sample data."""
    data_dir = Path(__file__).parent / "data"
    
    print("🌱 Starting database seeding...")
    
    try:
        # 1. Seed projections
        print("📊 Seeding projections...")
        projections = await ingest_projections_csv(str(data_dir / "projections_2024.csv"))
        await update_projections_db(projections)
        
        # 2. Seed historical stats
        print("📈 Seeding historical stats...")
        stats = await ingest_stats_csv(str(data_dir / "historical_stats_2023.csv"))
        await update_stats_db(stats)
        
        # 3. Seed injuries
        print("🏥 Seeding injuries...")
        injuries = await ingest_injuries_csv(str(data_dir / "injuries.csv"))
        await update_injuries_db(injuries)
        
        # 4. Seed depth charts
        print("📋 Seeding depth charts...")
        depth_data = await ingest_depth_csv(str(data_dir / "depth_charts.csv"))
        await update_depth_db(depth_data)
        
        # 5. Seed ADP
        print("🎯 Seeding ADP data...")
        adp_data = await ingest_adp_csv(str(data_dir / "adp.csv"))
        await update_adp_db(adp_data)
        
        print("✅ Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_database())