from enum import Enum

class GenderTypeEnum(str, Enum):
    MALE = 'male',
    FEMALE = 'female',
    OTHER = 'other'