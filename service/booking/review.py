from decimal import Decimal
from typing import Optional, List

from fastapi import HTTPException, Query, Response, Request, status
from sqlalchemy.orm import joinedload
from sqlalchemy import select, insert, update, func, literal, case, and_

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination, AuthenticatedUser
from models import User, Review, UserCounters, ReviewLike, ReviewProductOwnerLike, Service, Product, Appointment
from schema.booking.review import ReviewCreate, ReviewSummaryResponse, RatingBreakdown, UserReviewResponse, \
    ReviewResponse, ReviewUpdate

async def _apply_rating_change(
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

    counters = (await db.execute(select(uc).where(uc.user_id == user_id))).scalars().first()
    return counters

async def get_reviews_by_user_id(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        auth_user: AuthenticatedUser,
        ratings: Optional[List[int]] = Query(None)
) -> PaginatedResponse[UserReviewResponse]:
    auth_user_id = auth_user.id

    stmt = select(Review).where(
        Review.user_id == user_id,
        Review.parent_id.is_(None)
    )

    if ratings:
        stmt = stmt.where(
            Review.rating.in_(ratings)
        )

    stmt = (
        stmt
        .options(
            joinedload(Review.business_or_employee).load_only(User.id, User.username, User.fullname, User.avatar),
            joinedload(Review.customer).load_only(User.id, User.username, User.fullname, User.avatar),
            joinedload(Review.service).load_only(Service.id, Service.name),
            joinedload(Review.product).load_only(Product.id, Product.name)
        )
        .offset((pagination.page - 1) * pagination.limit)
        .limit(pagination.limit)
        .order_by(Review.created_at.asc()))

    total_count = await db.execute(select(func.count()).select_from(stmt.subquery()))
    count: int = total_count.scalars().first()

    reviews_result = await db.execute(stmt)
    reviews = reviews_result.scalars().unique().all()

    # Get Likes by the Authenticated User
    user_likes_query = await db.execute(
        select(ReviewLike.review_id)
        .where(ReviewLike.user_id == auth_user_id)
    )
    user_liked_reviews: List[int] = user_likes_query.scalars().all()

    # Get Post Author Likes
    product_owner_query = await db.execute(
        select(ReviewProductOwnerLike.product_owner_id)
        .where(Review.user_id == user_id)
    )
    product_owner_id: List[int] = product_owner_query.scalar()

    # Get Product Author Likes
    product_owner_likes = await db.execute(
        select(ReviewProductOwnerLike.review_id)
        .where(ReviewProductOwnerLike.product_owner_id == product_owner_id)
    )
    product_owner_liked_reviews: List[int] = product_owner_likes.scalars().all()

    return PaginatedResponse(
        count=count,
        results=[
            UserReviewResponse(
                id=review.id,
                rating=review.rating,
                review=review.review,
                product_business_owner=review.business_or_employee,
                customer=review.customer,
                service=review.service,
                product=review.product,
                like_count=review.like_count,
                is_liked=review.id in user_liked_reviews,
                is_liked_by_product_owner=review.id in product_owner_liked_reviews,
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

    breakdown: List[RatingBreakdown] = [
        RatingBreakdown(rating=i, count=breakdown_dict.get(i, 0))
        for i in range(5, 0, -1)
    ]

    return ReviewSummaryResponse(
        average_rating=round(float(average_rating), 1),
        total_reviews=total_reviews,
        breakdown=breakdown
    )

async def create_new_review(
        db: DBSession,
        appointment_id: int,
        review_create: ReviewCreate,
        auth_user: AuthenticatedUser
) -> ReviewResponse:
    async with db.begin():
        auth_user_id = auth_user.id
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
            await _apply_rating_change(
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
    auth_user: AuthenticatedUser
) -> ReviewResponse:
    async with db.begin():
        auth_user_id = auth_user.id
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
            await _apply_rating_change(
                db=db,
                user_id=review.user_id,
                delta_count=0,
                delta_sum=Decimal(review_update.rating - review.rating)
            )

        return review

async def delete_review_by_id(
        db: DBSession,
        review_id: int,
        auth_user: AuthenticatedUser
) -> Response:
    async with db.begin():
        auth_user_id = auth_user.id

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

        await _apply_rating_change(
            db=db,
            user_id=review.user_id,
            delta_count=-1,
            delta_sum=-review.rating
        )

        # Update Appointment
        appointment.has_written_review = False
        db.add(appointment)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

async def like_review_by_id(
        db: DBSession,
        review_id: int,
        auth_user: AuthenticatedUser
) -> Response:
    async with db.begin():
        auth_user_id = auth_user.id
        review: Review = await db.get(Review, review_id)

        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Review not found')

        stmt = await db.execute(
            select(ReviewLike)
            .where(
                ReviewLike.review_id == review_id,
                ReviewLike.user_id == auth_user_id
            )
        )

        liked: ReviewLike = stmt.scalar()

        if liked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Review already liked')

        is_product_owner: bool = auth_user_id == review.user_id

        # Insert User Like
        await db.execute(
            insert(ReviewLike)
            .values(
                review_id=review_id,
                user_id=auth_user_id
            )
        )

        # Update Review Counter
        await db.execute(
            update(Review)
            .where(Review.id == review_id)
            .values(like_count=Review.like_count + 1)
        )

        # Insert Like into ReviewProductOwnerLike
        if is_product_owner:
            await db.execute(
                insert(ReviewProductOwnerLike)
                .values(
                    review_id=review_id,
                    product_owner_id=auth_user_id
                )
            )

    return Response(status_code=status.HTTP_201_CREATED)

async def unlike_review_by_id(
        db: DBSession,
        review_id: int,
        auth_user: AuthenticatedUser
) -> Response:
    async with db.begin():
        auth_user_id = auth_user.id
        review: Review = await db.get(Review, review_id)

        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Review not found')

        query = await db.execute(
            select(ReviewLike)
            .where(and_(
                ReviewLike.review_id == review_id,
                ReviewLike.user_id == auth_user_id
            ))
        )

        liked: ReviewLike = query.scalar()

        if liked is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Review is not liked')

        is_product_owner: bool = auth_user_id == review.user_id

        # Delete Like
        await db.delete(liked)

        # Update Review Counter
        await db.execute(
            update(Review)
            .where(Review.id == review_id)
            .values(like_count=Review.like_count - 1)
        )

        # Delete Like from ReviewProductOwnerLike
        if is_product_owner:
            query = await db.execute(
                select(ReviewProductOwnerLike)
                .where(and_(
                    ReviewProductOwnerLike.review_id == review_id,
                    ReviewProductOwnerLike.product_owner_id == auth_user_id
                ))
            )
            product_owner_like = query.scalar()
            await db.delete(product_owner_like)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


