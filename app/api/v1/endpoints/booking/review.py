from fastapi import APIRouter
from starlette.requests import Request
from fastapi import status
from app.core.dependencies import DBSession
from app.schema.booking.review import ReviewResponse, ReviewCreate
from app.service.booking.review import create_new_review, like_review_by_id, unlike_review_by_id

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=ReviewResponse)
async def create_review(db: DBSession, review_data: ReviewCreate, request :Request):
    return await create_new_review(db, review_data, request)

@router.post("/{review_id}/likes", status_code=status.HTTP_201_CREATED)
async def like_review(db: DBSession, review_id: int, request: Request):
    return await like_review_by_id(db, review_id, request)

@router.delete("/{review_id}/likes", status_code=status.HTTP_204_NO_CONTENT)
async def like_review(db: DBSession, review_id: int, request: Request):
    return await unlike_review_by_id(db, review_id, request)
