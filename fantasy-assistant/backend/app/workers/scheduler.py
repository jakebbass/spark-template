"""Background job scheduler for data ingestion."""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from app.services.ingest_projections import ingest_projections_api, update_projections_db
from app.services.ingest_injuries import ingest_injuries_api, update_injuries_db
from app.services.ingest_depth import ingest_depth_csv, update_depth_db
from app.services.ingest_stats_last_year import ingest_stats_csv, update_stats_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def job_update_projections():
    """Job to update player projections."""
    logger.info("Starting projections update job")
    try:
        projections = await ingest_projections_api()
        await update_projections_db(projections)
        logger.info(f"Updated {len(projections)} projections")
    except Exception as e:
        logger.error(f"Error updating projections: {e}")


async def job_update_injuries():
    """Job to update injury data."""
    logger.info("Starting injuries update job")
    try:
        injuries = await ingest_injuries_api()
        await update_injuries_db(injuries)
        logger.info(f"Updated {len(injuries)} injury reports")
    except Exception as e:
        logger.error(f"Error updating injuries: {e}")


async def job_update_depth_charts():
    """Job to update depth charts."""
    logger.info("Starting depth charts update job")
    try:
        depth_data = await ingest_depth_csv("data/depth_charts.csv")
        await update_depth_db(depth_data)
        logger.info(f"Updated {len(depth_data)} depth chart entries")
    except Exception as e:
        logger.error(f"Error updating depth charts: {e}")


def setup_jobs():
    """Setup scheduled jobs."""
    # Nightly projections update
    scheduler.add_job(
        job_update_projections,
        CronTrigger(hour=2, minute=0),  # 2 AM daily
        id='update_projections',
        name='Update Player Projections',
        replace_existing=True
    )
    
    # Injury updates every 5 minutes during season
    scheduler.add_job(
        job_update_injuries,
        CronTrigger(minute='*/5'),  # Every 5 minutes
        id='update_injuries',
        name='Update Injury Reports',
        replace_existing=True
    )
    
    # Weekly depth chart updates
    scheduler.add_job(
        job_update_depth_charts,
        CronTrigger(day_of_week=1, hour=6, minute=0),  # Mondays at 6 AM
        id='update_depth_charts',
        name='Update Depth Charts',
        replace_existing=True
    )


async def start_scheduler():
    """Start the job scheduler."""
    setup_jobs()
    scheduler.start()
    logger.info("Job scheduler started")
    
    try:
        # Keep the scheduler running
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("Stopping scheduler")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(start_scheduler())