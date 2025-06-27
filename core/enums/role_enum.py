from enum import Enum

class RoleEnum(str, Enum):
    CLIENT = "client",
    EMPLOYEE = "employee",
    BUSINESS = "business",
    SUPER_ADMIN = "superadmin",
    MANAGER = "manager"