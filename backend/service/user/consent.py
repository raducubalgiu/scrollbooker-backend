from backend.core.crud_helpers import db_create, db_get_one
from backend.core.dependencies import DBSession
from backend.schema.user.consent import ConsentCreate
from backend.models import Consent

async def get_consent_by_name(db: DBSession, consent_name: str):
    return await db_get_one(db, model=Consent, filters={Consent.name: consent_name})

async def create_new_consent(db: DBSession, consent_create: ConsentCreate):
    return await db_create(db, model= Consent, create_data=consent_create)