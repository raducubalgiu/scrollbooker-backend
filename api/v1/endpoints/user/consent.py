from fastapi import APIRouter

from backend.core.dependencies import SuperAdminSession, DBSession
from backend.schema.nomenclature.consent import ConsentResponse, ConsentCreate
from backend.service.nomenclature.consent import get_consent_by_name, create_new_consent

router = APIRouter(prefix="/consents", tags=["Consents"])

@router.get(
    "/{consent_name}",
    summary='List All Consents Filtered By Consent Name',
    response_model=ConsentResponse)
async def get_consent(db: DBSession, consent_name: str):
    return await get_consent_by_name(db, consent_name)

@router.post(
    "/",
    summary='Create New Consent',
    response_model=ConsentResponse,
    dependencies=[SuperAdminSession])
async def create_consent(db: DBSession, consent_create: ConsentCreate):
    return await create_new_consent(db, consent_create)