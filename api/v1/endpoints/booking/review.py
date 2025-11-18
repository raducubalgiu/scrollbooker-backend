from typing import Optional, List

from fastapi import APIRouter, Query, status, Request, Response

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination, ClientAndEmployeeSession, AuthenticatedUser
from schema.booking.review import ReviewResponse, ReviewCreate, ReviewSummaryResponse, UserReviewResponse, ReviewUpdate
from service.booking.review import create_new_review, like_review_by_id, unlike_review_by_id, \
    get_reviews_by_user_id, get_reviews_summary_by_user_id, delete_review_by_id, update_review_by_id

router = APIRouter(tags=["Reviews"])

@router.get("/users/{user_id}/reviews",
    summary='List All Reviews By User Id - Business Or Employee',
    response_model=PaginatedResponse[UserReviewResponse])
async def get_author_reviews(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        auth_user: AuthenticatedUser,
        ratings: Optional[List[int]] = Query(None),
) -> PaginatedResponse[UserReviewResponse]:
    return await get_reviews_by_user_id(db, user_id, pagination, auth_user, ratings)

@router.get("/users/{user_id}/reviews-summary",
    summary='List Reviews Summary By User Id - Business Or Employee',
    response_model=ReviewSummaryResponse)
async def get_reviews_summary(db: DBSession, user_id: int) -> ReviewSummaryResponse:
    return await get_reviews_summary_by_user_id(db, user_id)

@router.post("/appointments/{appointment_id}/create-review",
    summary='Create New Review',
    dependencies=[ClientAndEmployeeSession],
    response_model=ReviewResponse)
async def create_review(
        db: DBSession,
        appointment_id: int,
        review_create: ReviewCreate,
        auth_user: AuthenticatedUser
) -> ReviewResponse:
    return await create_new_review(db, appointment_id, review_create, auth_user)

@router.delete("/reviews/{review_id}",
       summary='Delete Review',
       dependencies=[ClientAndEmployeeSession],
       status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(db: DBSession, review_id: int, auth_user: AuthenticatedUser) -> Response:
    return await delete_review_by_id(db, review_id, auth_user)

@router.patch("/reviews/{review_id}",
      summary='Update Review By Id',
      dependencies=[ClientAndEmployeeSession],
      response_model=ReviewResponse)
async def update_review(
        db: DBSession,
        review_id: int,
        review_update: ReviewUpdate,
        auth_user: AuthenticatedUser
) -> ReviewResponse:
    return await update_review_by_id(db, review_id, review_update, auth_user)

@router.post("/reviews/{review_id}/likes",
    summary='Like Review',
    status_code=status.HTTP_201_CREATED)
async def like_review(db: DBSession, review_id: int, auth_user: AuthenticatedUser) -> Response:
    return await like_review_by_id(db, review_id, auth_user)

@router.delete("/reviews/{review_id}/likes",
    summary='Unlike Review',
    status_code=status.HTTP_204_NO_CONTENT)
async def unlike_review(db: DBSession, review_id: int, auth_user: AuthenticatedUser) -> Response:
    return await unlike_review_by_id(db, review_id, auth_user)
