from fastapi import APIRouter
from starlette.requests import Request
from fastapi import status
from backend.core.dependencies import DBSession
from backend.schema.booking.review import ReviewResponse, ReviewCreate
from backend.service.booking.review import create_new_review, like_review_by_id, unlike_review_by_id, \
    get_review_by_user_id

router = APIRouter(tags=["Reviews"])

@router.get("/users/{user_id}/reviews",
    summary='List All Reviews By User Id - Business Or Employee')
async def get_author_reviews(db: DBSession, user_id: int, page: int, limit: int, request: Request):
    return await get_review_by_user_id(db, user_id, page, limit, request)

@router.post("/reviews",
    summary='Create New Review',
    response_model=ReviewResponse)
async def create_review(db: DBSession, review_data: ReviewCreate, request :Request):
    return await create_new_review(db, review_data, request)

@router.post("/reviews/{review_id}/likes",
    summary='Like Review',
    status_code=status.HTTP_201_CREATED)
async def like_review(db: DBSession, review_id: int, request: Request):
    return await like_review_by_id(db, review_id, request)

@router.delete("/reviews/{review_id}/likes",
    summary='Unlike Review',
    status_code=status.HTTP_204_NO_CONTENT)
async def unlike_review(db: DBSession, review_id: int, request: Request):
    return await unlike_review_by_id(db, review_id, request)
