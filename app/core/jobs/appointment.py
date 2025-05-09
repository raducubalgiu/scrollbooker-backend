from app.core.database import async_session_factory
from app.core.enums.enums import AppointmentStatusEnum
from app.core.logger import logger
from sqlalchemy import select, and_
from datetime import datetime, timezone

from app.models import Appointment

async def update_appointment_status():
    async with async_session_factory() as db:
        try:
            now = datetime.now(timezone.utc)
            appointments_result = await db.execute(
                select(Appointment).where(and_(
                    Appointment.start_date <= now,
                    Appointment.status == AppointmentStatusEnum.IN_PROGRESS
                ))
            )
            appointments = appointments_result.scalars().all()

            logger.info(f"[Scheduler] {now.isoformat()} - Found {len(appointments)} appointments to update")

            for a in appointments:
                a.status = AppointmentStatusEnum.FINISHED

            await db.commit()
            logger.info(f"[Scheduler] Appointments updated successfully.")

        except Exception as e:
            logger.error(f"[Scheduler] Error while updating appointments: {str(e)}")