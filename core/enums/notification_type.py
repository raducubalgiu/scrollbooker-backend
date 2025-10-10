from enum import Enum

class NotificationTypeEnum(str, Enum):
    FOLLOW = "follow"
    EMPLOYMENT_REQUEST = "employment_request"
    EMPLOYMENT_REQUEST_ACCEPT = "employment_request_accept"
    EMPLOYMENT_REQUEST_DENIED = "employment_request_denied"

