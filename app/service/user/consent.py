from app.core.crud_helpers import db_create, db_get_one
from app.core.dependencies import DBSession
from app.schema.user.consent import ConsentCreate
from app.models import Consent

async def get_consent_by_name(db: DBSession, consent_name: str):
    return await db_get_one(db, model=Consent, filters={Consent.name: consent_name})

async def create_new_consent(db: DBSession, consent_create: ConsentCreate):
    return await db_create(db, model= Consent, create_data=consent_create)