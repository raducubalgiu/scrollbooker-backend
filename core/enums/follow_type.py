from enum import Enum

class FollowTypeEnum(str, Enum):
    FOLLOW = "FOLLOW"
    UNFOLLOW = "UNFOLLOW"