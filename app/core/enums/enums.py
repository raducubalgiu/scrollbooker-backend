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