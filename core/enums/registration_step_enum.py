from enum import Enum

class RegistrationStepEnum(str, Enum):
    COLLECT_EMAIL_VERIFICATION = "collectEmailVerification"

    COLLECT_USERNAME = 'collectUsername'
    COLLECT_PHONE_NUMBER = 'collectPhoneNumber'
    COLLECT_CLIENT_BIRTH_DATE = 'collectClientBirthdate'
    COLLECT_CLIENT_GENDER = 'collectClientGender'

    COLLECT_LOCATION_PERMISSION = 'collectClientLocationPermission'

    COLLECT_BUSINESS_TYPE = "collect_business_type"
    COLLECT_BUSINESS_LOCATION = "collect_business_location"
    COLLECT_BUSINESS_SERVICES = "collect_business_services"
    COLLECT_BUSINESS_SCHEDULES = "collect_business_schedules"