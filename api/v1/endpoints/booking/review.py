from typing import Optional, List

from fastapi import APIRouter, Query
from starlette.requests import Request
from fastapi import status

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession
from backend.schema.booking.review import ReviewResponse, ReviewCreate, ReviewSummaryResponse, \
    UserReviewResponse
from backend.service.booking.review import create_new_review, like_review_by_id, unlike_review_by_id, \
    get_reviews_by_user_id, get_reviews_summary_by_user_id

router = APIRouter(tags=["Reviews"])

@router.get("/users/{user_id}/reviews",
    summary='List All Reviews By User Id - Business Or Employee',
    response_model=PaginatedResponse[UserReviewResponse])
async def get_author_reviews(
        db: DBSession,
        user_id: int,
        page: int,
        limit: int,
        request: Request,
        ratings: Optional[List[int]] = Query(None),
):
    return await get_reviews_by_user_id(db, user_id, page, limit, request, ratings)

@router.get("/users/{user_id}/reviews-summary",
    summary='List Reviews Summary By User Id - Business Or Employee',
    response_model=ReviewSummaryResponse)
async def get_reviews_summary(db: DBSession, user_id: int):
    return await get_reviews_summary_by_user_id(db, user_id)

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
