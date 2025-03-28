from datetime import datetime, date, time
from typing import Optional
import pytz  # type: ignore
from app.core.logger import logger

async def local_to_utc_fulldate(timezone: str, local_date: str, local_time: str):
    try:
        date_obj = datetime.strptime(local_date, "%Y-%m-%d").date()
        time_obj = datetime.strptime(local_time, "%H:%M:%S").time()
        full_date = datetime.combine(date_obj, time_obj)
        full_date_utc = pytz.timezone(timezone).localize(full_date).astimezone(pytz.utc)
        return full_date_utc

    except Exception as e:
        raise ValueError(f"Error converting date: '{local_date}' and time: '{local_time}' with timezone '{timezone}'. Error: {e}")

async def local_to_utc(timezone: str, local_time: Optional[str] = None, day: datetime = date.today()):
    try:
        if not local_time:
            return None

        today = day
        local_tz = pytz.timezone(timezone)

        # Parse and localize
        local_dt = datetime.strptime(f"{today} {local_time}", f"%Y-%m-%d %H:%M:%S")
        local_dt = local_tz.localize(local_dt)

        # Convert to UTC
        return local_dt.astimezone(pytz.utc)
    except Exception as e:
        logger.error(f"Error converting time '{local_time}' with timezone '{timezone}'. Error: {e}")
        raise ValueError(f"Error converting time '{local_time}' with timezone '{timezone}'. Error: {e}")

async def utc_to_local(timezone: str, utc_time: str, day: datetime = date.today()):
    try:
        local_tz = pytz.timezone(timezone)
        today = day

        # Convert UTC string to datetime
        local_dt = pytz.utc.localize(datetime.strptime(f"{today} {utc_time}", "%Y-%m-%d %H:%M:%S"))

        # Convert to local timezone
        local = local_dt.astimezone(local_tz)

        return local.strftime("%H:%M:%S")

    except Exception as e:
        logger.error(f"Error converting utc time '{utc_time}'. Error: {e}")
        raise ValueError(f"Error converting utc time '{utc_time}'.Error: {e}")

async def from_string_to_time(time_str: str, format: str = "%H:%M:%S") -> time:
    try:
        return datetime.strptime(time_str, format).time()
    except Exception as e:
        logger.error(f"Time string '{time_str}' does not match format '{format}'. Error: {e}")
        raise ValueError(f"Time string '{time_str}' does not match format '{format}'") from e

