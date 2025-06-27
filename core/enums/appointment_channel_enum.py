from enum import Enum

class AppointmentChannelEnum(str, Enum):
    OWN_CLIENT = "own_client",
    SCROLL_BOOKER = "scroll_booker"