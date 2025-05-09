from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.jobs.appointment import update_appointment_status

scheduler = AsyncIOScheduler()

def start():
    scheduler.add_job(update_appointment_status, "interval", minutes=1)
    scheduler.start()