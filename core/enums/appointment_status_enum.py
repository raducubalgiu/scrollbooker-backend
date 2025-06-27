from enum import Enum

class AppointmentStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELED = "canceled"