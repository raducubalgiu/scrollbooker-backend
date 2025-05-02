from enum import Enum

class PostAction(str, Enum):
    LIKE = "like",
    SAVE = "save",
    SHARE = "share"

class RoleEnum(str, Enum):
    CLIENT = "client",
    EMPLOYEE = "employee",
    BUSINESS = "business",
    SUPER_ADMIN = "superadmin"

class ChannelEnum(str, Enum):
    OWN_CLIENT = "own_client",
    SCROLL_BOOKER = "scroll_booker"

class AppointmentStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress",
    FINISHED = "finished"
