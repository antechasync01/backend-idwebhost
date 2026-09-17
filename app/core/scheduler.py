"""Background scheduler for periodic tasks."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import SessionLocal
from app.modules.events.application.events_service import EventsService

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def sync_and_analyze_calendar_events():
    """Job to sync calendar events and analyze new ones via Hermes Agent."""
    logger.info("Starting scheduled calendar sync and analysis...")
    db = SessionLocal()
    try:
        service = EventsService(db)
        # Fetch 30 days ahead as requested
        synced, analyzed = service.sync_and_analyze(days_ahead=30, days_behind=0)
        logger.info(f"Scheduled sync complete. Synced: {synced}, Analyzed: {analyzed}")
    except Exception as e:
        logger.error(f"Error during scheduled calendar sync: {e}")
    finally:
        db.close()

def generate_weekly_sales_analysis():
    """Job to generate weekly sales analysis using Hermes Agent."""
    logger.info("Starting scheduled weekly sales analysis...")
    from app.modules.analytics.application.periodic_analysis_service import PeriodicAnalysisService
    from app.modules.analytics.infrastructure.models import AnalysisPeriod
    
    db = SessionLocal()
    try:
        service = PeriodicAnalysisService(db)
        service.generate_analysis(AnalysisPeriod.WEEKLY)
        logger.info("Scheduled weekly sales analysis complete.")
    except Exception as e:
        logger.error(f"Error during scheduled weekly sales analysis: {e}")
    finally:
        db.close()


def generate_monthly_sales_analysis():
    """Job to generate monthly sales analysis using Hermes Agent."""
    logger.info("Starting scheduled monthly sales analysis...")
    from app.modules.analytics.application.periodic_analysis_service import PeriodicAnalysisService
    from app.modules.analytics.infrastructure.models import AnalysisPeriod
    
    db = SessionLocal()
    try:
        service = PeriodicAnalysisService(db)
        service.generate_analysis(AnalysisPeriod.MONTHLY)
        logger.info("Scheduled monthly sales analysis complete.")
    except Exception as e:
        logger.error(f"Error during scheduled monthly sales analysis: {e}")
    finally:
        db.close()


def start_scheduler():
    """Configure and start the background scheduler."""
    # Existing job for calendar
    scheduler.add_job(
        sync_and_analyze_calendar_events,
        trigger=CronTrigger(day=1, hour=0, minute=0),
        id="sync_calendar_monthly",
        name="Monthly Google Calendar Sync and Analyze",
        replace_existing=True
    )
    
    # Weekly sales analysis (Every Monday at 01:00)
    scheduler.add_job(
        generate_weekly_sales_analysis,
        trigger=CronTrigger(day_of_week='mon', hour=1, minute=0),
        id="weekly_sales_analysis",
        name="Weekly Sales Analysis",
        replace_existing=True
    )

    # Monthly sales analysis (1st of every month at 02:00)
    scheduler.add_job(
        generate_monthly_sales_analysis,
        trigger=CronTrigger(day=1, hour=2, minute=0),
        id="monthly_sales_analysis",
        name="Monthly Sales Analysis",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Background scheduler started with jobs: Calendar, Weekly Sales, Monthly Sales.")

def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    logger.info("Background scheduler stopped.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager for background tasks."""
    start_scheduler()
    yield
    stop_scheduler()
