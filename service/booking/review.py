from decimal import Decimal
from typing import Optional, List

from fastapi import HTTPException, Query, Response, Request, status
from sqlalchemy.orm import joinedload
from sqlalchemy import select, insert, update, func, literal, case

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession
from models import User, Review, UserCounters, ReviewLike, ReviewProductLike, Service, Product, Appointment
from schema.booking.review import ReviewCreate, ReviewSummaryResponse, RatingBreakdown, UserReviewResponse, \
    ReviewResponse, ReviewUpdate
from core.logger import logger

async def get_reviews_by_user_id(
        db: DBSession,
        user_id: int,
        page: int, limit: int,
        request: Request,
        ratings: Optional[List[int]] = Query(None)
) -> PaginatedResponse[UserReviewResponse]:
    auth_user_id = request.state.user.get("id")

    reviews_stmt = select(Review).where(
        Review.user_id == user_id,
        Review.parent_id.is_(None)
    )

    if ratings:
        reviews_stmt = reviews_stmt.where(
            Review.rating.in_(ratings)
        )

    reviews_stmt = (
        reviews_stmt
        .options(
            joinedload(Review.customer).load_only(User.id, User.username, User.fullname, User.avatar),
            joinedload(Review.service).load_only(Service.id, Service.name),
            joinedload(Review.product).load_only(Product.id, Product.name)
        )
        .offset((page - 1) * limit)
        .limit(limit)
        .order_by(Review.created_at.asc()))


    count_reviews = await db.execute(reviews_stmt)
    count = len(count_reviews.all())

    reviews_result = await db.execute(reviews_stmt)
    reviews = reviews_result.scalars().unique().all()

    # Get Likes by the Authenticated User
    user_likes_query = await db.execute(
        select(ReviewLike.review_id)
        .where(ReviewLike.user_id == auth_user_id)
    )
    user_liked_reviews = user_likes_query.scalars().all()

    # Get Post Author Likes
    product_author_query = await db.execute(
        select(ReviewProductLike.product_author_user_id)
        .where(Review.user_id == user_id)
    )
    product_author_id = product_author_query.scalar()

    # Get Product Author Likes
    product_author_likes = await db.execute(
        select(ReviewProductLike.review_id)
        .where(ReviewProductLike.product_author_user_id == product_author_id)
    )
    product_author_liked_reviews = product_author_likes.scalars().all()

    return PaginatedResponse(
        count=count,
        results=[
            UserReviewResponse(
                id=review.id,
                rating=review.rating,
                review=review.review,
                customer=review.customer,
                service=review.service,
                product=review.product,
                like_count=review.like_count,
                is_liked=review.id in user_liked_reviews,
                is_liked_by_author=review.id in product_author_liked_reviews,
                created_at=review.created_at
            ) for review in reviews
        ]
    )

async def get_reviews_summary_by_user_id(
        db: DBSession,
        user_id
) -> ReviewSummaryResponse:
    result = await db.execute(
        select(
            func.count(Review.id),
            func.avg(Review.rating)
        )
        .where(Review.user_id == user_id)
    )

    total_reviews, average_rating = result.first()

    if total_reviews == 0:
        return ReviewSummaryResponse(
            average_rating=0.0,
            total_reviews=0,
            breakdown=[RatingBreakdown(rating=i, count=0) for i in range(5, 0, -1)]
        )

    breakdown_result = await db.execute(
        select(
            Review.rating,
            func.count(Review.id)
        )
        .where(Review.user_id == user_id)
        .group_by(Review.rating)
    )

    breakdown_dict = { rating: count for rating, count in breakdown_result.all() }

    breakdown = [
        RatingBreakdown(rating=i, count=breakdown_dict.get(i, 0))
        for i in range(5, 0, -1)
    ]

    return ReviewSummaryResponse(
        average_rating=round(float(average_rating), 1),
        total_reviews=total_reviews,
        breakdown=breakdown
    )

async def apply_rating_change(
    db: DBSession,
    user_id: int,
    delta_count: int,
    delta_sum: Decimal,
) -> UserCounters:
    uc = UserCounters

    count_new_expr = uc.ratings_count + literal(delta_count)

    numerator_expr = (uc.ratings_average * uc.ratings_count) + literal(delta_sum)
    denom_expr = func.nullif(count_new_expr, 0)

    avg_new_expr = case(
        (count_new_expr > 0, numerator_expr / denom_expr),
        else_=literal(0.0)
    )

    stmt = (
        update(uc)
        .where(uc.user_id == user_id)
        .values(
            ratings_count=count_new_expr,
            ratings_average=avg_new_expr,
        )
        .returning(uc.user_id, uc.ratings_count, uc.ratings_average)
    )

    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Counters not found",
        )

    obj = (await db.execute(select(uc).where(uc.user_id == user_id))).scalars().first()
    return obj


async def create_new_review(
        db: DBSession,
        appointment_id: int,
        review_create: ReviewCreate,
        request: Request
) -> ReviewResponse:
    async with db.begin():
        auth_user_id = request.state.user.get("id")
        appointment: Appointment = await db.get(Appointment, appointment_id)

        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        product: Product = await db.get(Product, review_create.product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Create Review
        review = Review(
            **review_create.model_dump(),
            appointment_id=appointment_id,
            service_id=product.service_id,
            customer_id=auth_user_id
        )
        db.add(review)
        await db.flush()

        # Update User Counters
        if review_create.parent_id is None:
            await apply_rating_change(
                db=db,
                user_id=review.user_id,
                delta_count=1,
                delta_sum=review.rating
            )

        # Update Appointment
        appointment.has_written_review = True
        db.add(appointment)

        return review

async def update_review_by_id(
    db: DBSession,
    review_id: int,
    review_update: ReviewUpdate,
    request: Request
) -> ReviewResponse:
    async with db.begin():
        auth_user_id = request.state.user.get("id")
        review: Review = await db.get(Review, review_id)

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        if review.customer_id != auth_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )

        appointment: Appointment = await db.get(Appointment, review.appointment_id)

        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        # Update Review
        review.rating = review_update.rating
        review.review = review_update.review

        db.add(review)
        await db.flush()

        if review_update.rating != review.rating:
            await apply_rating_change(
                db=db,
                user_id=review.user_id,
                delta_count=0,
                delta_sum=Decimal(review_update.rating - review.rating)
            )

        return review

async def delete_review_by_id(
        db: DBSession,
        review_id: int,
        request: Request
) -> Response:
    async with db.begin():
        auth_user_id = request.state.user.get("id")

        review: Review = await db.get(Review, review_id)
        appointment: Appointment = await db.get(Appointment, review.appointment_id)

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Review not found'
            )

        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Appointment not found'
            )

        if review.user_id != auth_user_id and review.customer_id != auth_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You do not have permission to perform this action'
            )

        await db.delete(review)

        await apply_rating_change(
            db=db,
            user_id=review.user_id,
            delta_count=-1,
            delta_sum=-review.rating
        )

        # Update Appointment
        appointment.has_written_review = False
        db.add(appointment)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

async def like_review_by_id(db: DBSession, review_id: int, request: Request):
    auth_user_id = request.state.user.get("id")
    review = await db.get(Review, review_id)

    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Review not found')

    query = await db.execute(
        select(ReviewLike)
        .where(
            ReviewLike.review_id == review_id,
            ReviewLike.user_id == auth_user_id
        )
    )

    liked = query.scalar()

    if liked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Review already liked')

    is_author_business_or_employee = auth_user_id == review.user_id

    try:
        await db.execute(insert(ReviewLike).values(review_id=review_id, user_id=auth_user_id))

        await db.execute(
            update(Review)
            .where(Review.id == review_id)
            .values(like_count=Review.like_count + 1)
        )

        if is_author_business_or_employee:
            await db.execute(
                insert(ReviewProductLike)
                .values(review_id=review_id, product_author_user_id=auth_user_id)
            )

        await db.commit()
        return {"detail": "Review liked!"}

    except Exception as e:
        await db.rollback()
        logger.error(f"Review could not be liked. Error: {e}")

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')

async def unlike_review_by_id(
        db: DBSession,
        review_id: int, request: Request
):
    auth_user_id = request.state.user.get("id")
    review = await db.get(Review, review_id)

    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Review not found')
    query = await db.execute(
        select(ReviewLike)
        .where((ReviewLike.review_id == review_id) & (ReviewLike.user_id == auth_user_id))  # type: ignore
    )

    liked = query.scalar()

    if liked is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Review is not liked')

    is_author_business_or_employee = auth_user_id == review.user_id

    try:
        await db.delete(liked)

        await db.execute(
            update(Review)
            .where(Review.id == review_id)  # type: ignore
            .values(like_count=Review.like_count - 1)
        )
        if is_author_business_or_employee:
            query = await db.execute(
                select(ReviewProductLike)
                .where(
                    (ReviewProductLike.review_id == review_id) & (ReviewProductLike.product_author_user_id == auth_user_id)) #type: ignore
            )
            product_author_like = query.scalar()
            await db.delete(product_author_like)

        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Review could not be unliked. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')
