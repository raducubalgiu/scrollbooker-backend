from enum import Enum

class RegistrationStepEnum(str, Enum):
    COLLECT_USER_EMAIL_VALIDATION = "collect_user_email_validation"
    COLLECT_USER_USERNAME = 'collect_user_username'
    COLLECT_USER_PHONE_NUMBER = 'collect_user_phone_number'

    COLLECT_CLIENT_BIRTHDATE = 'collect_client_birthdate'
    COLLECT_CLIENT_GENDER = 'collect_client_gender'
    COLLECT_CLIENT_LOCATION_PERMISSION = 'collect_client_location_permission'

    COLLECT_BUSINESS = "collect_business"
    COLLECT_BUSINESS_SERVICES = "collect_business_services"
    COLLECT_BUSINESS_SCHEDULES = "collect_business_schedules"
    COLLECT_BUSINESS_HAS_EMPLOYEES = "collect_business_has_employees"
    COLLECT_BUSINESS_CURRENCIES = "collect_business_currencies"
    COLLECT_BUSINESS_VALIDATION = "collect_business_validation"