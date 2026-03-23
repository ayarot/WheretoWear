from apscheduler.schedulers.background import BackgroundScheduler
import time
from zoneinfo import ZoneInfo
from jobs.snapshot_job import snapshot_job
from db.cities import get_all_cities
import logging

logger = logging.getLogger(__name__)
TARGET_HOURS = {10, 18}
scheduler = BackgroundScheduler()

#https://www.youtube.com/watch?v=XDgu2VKXM3s

def sync_jobs():
    logger.info("Syncing jobs with DB...")
    cities = get_all_cities()
    existing_jobs = {job.id for job in scheduler.get_jobs()}
    current_job = set()

    for city_id, name, country, url, timezone in cities:
        job_id = f"city_{city_id}"
        current_job.add(job_id)

        if job_id not in existing_jobs:
            scheduler.add_job(
                snapshot_job,
                trigger='cron',
                hour="10,18",
                minute="0",
                args=[name, url],
                timezone=timezone,
                id=job_id,
                replace_existing=True
            )
            logger.info(f"Added job for {name}")
    # Remove jobs that are no longer in the DB
    for job_id in existing_jobs - current_job:
        scheduler.remove_job(job_id)
        logger.info(f"Removed job {job_id}")
 

def start_scheduler():
    sync_jobs()
    scheduler.start()
    logger.info("Scheduler started")

def test_job():
    logger.info("TEST JOB RUNNING 🚀")

# def start_scheduler():
#     logger.info("Starting scheduler...")
#     scheduler.add_job(
#         snapshot_job,
#         trigger="interval",
#         seconds=10,  # כל 10 שניות
#         args=["Tokyo", "https://www.youtube.com/watch?v=DjdUEyjx8GM"],
#     )
#     scheduler.start()
#     logger.info("Scheduler started")
    
#     for job in scheduler.get_jobs():
#         logger.info(f"Job added: {job}")