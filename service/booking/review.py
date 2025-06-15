from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from starlette.requests import Request
from starlette import status
from sqlalchemy import select, insert, update
from backend.core.dependencies import DBSession
from backend.models import Business, User, Review, UserCounters, ReviewLike, ReviewProductLike, Service, Product
from backend.schema.booking.review import ReviewCreate
from backend.core.logger import logger

async def restrict_employee_and_business(db: DBSession, review_data: ReviewCreate, request: Request):
    auth_user_id = request.state.user.get("id")
    auth_user_role = request.state.user.get("role")
    user = await db.get(User, auth_user_id)

    if auth_user_role == 'business' and auth_user_id != review_data.user_id and review_data.parent_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You do not have permission to perform this action')

    if auth_user_role == 'employee':
        stmt = await db.execute(
            select(Business)
            .where(Business.id == user.employee_business_id) # type: ignore
            .options(joinedload(Business.services))
        )
        business = stmt.scalars().first()

        for service in business.services:
            if service.id == review_data.service_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail='You do not have permission to perform this action')

async def update_review_counters(db: DBSession, user_id: int, rating: int):
    result = await db.execute(
        select(UserCounters)
        .filter(UserCounters.user_id == user_id))  # type: ignore
    user_counters = result.scalars().first()

    if not user_counters:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User Counters not found')

    old_ratings_count = user_counters.ratings_count
    new_ratings_count = user_counters.ratings_count + 1
    new_ratings_average = (user_counters.ratings_average * old_ratings_count + rating) / new_ratings_count

    user_counters.ratings_average = new_ratings_average
    user_counters.ratings_count = new_ratings_count

# async def get_user_reviews_by_user_id(db: DBSession, user_id: int, page: int, size: int):
#     stmt = await db.execute(
#         select(User)
#         .filter(User.id == user_id) # type: ignore
#         .options(joinedload(User.role))
#     )
#     user = stmt.scalars().first()
#     role = user.role
#
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail='User not found!')
#
#     field = 'customer_id' if role == 'client' else 'user_id'
#
#     stmt = await db.execute(
#         select(Review)
#         .where(getattr(Review, field) == user_id) #type: ignore
#         .options(
#             joinedload(Review.service),
#         )
#         .offset((page - 1) * size)
#         .limit(size)
#     )
#
#     reviews = stmt.scalars().unique().all()
#     return reviews

async def create_new_review(db: DBSession, review_data: ReviewCreate, request: Request):
    auth_user_id = request.state.user.get("id")
    await restrict_employee_and_business(db, review_data, request)

    try:
        # Create Review
        review = Review(**review_data.model_dump(), customer_id=auth_user_id)
        db.add(review)
        await db.flush()

        # Update User Counters
        if review_data.parent_id is None:
            await update_review_counters(db, review.user_id, review.rating)

        await db.commit()
        return review

    except Exception as e:
        await db.rollback()
        logger.error(f"Review could not be created. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Something went wrong")

async def like_review_by_id(db: DBSession, review_id: int, request: Request):
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

    if liked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Review already liked')

    is_author_business_or_employee = auth_user_id == review.user_id

    try:
        await db.execute(insert(ReviewLike).values(review_id=review_id, user_id=auth_user_id))

        await db.execute(
            update(Review)
            .where(Review.id == review_id) #type: ignore
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

async def unlike_review_by_id(db: DBSession, review_id: int, request: Request):
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

async def get_review_by_user_id(db: DBSession, user_id: int, page: int, limit: int, request: Request):
    auth_user_id = request.state.user.get("id")

    reviews_stmt = (select(Review)
        .where(
            Review.user_id == user_id,
            Review.parent_id.is_(None)
        )
        .options(
            joinedload(Review.customer).load_only(User.id, User.username, User.fullname, User.avatar),
            joinedload(Review.service).load_only(Service.id, Service.name),
            joinedload(Review.product).load_only(Product.id, Product.name)
        )
        .offset((page - 1) * limit)
        .limit(limit)
        .order_by(Review.created_at.asc()))

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

    return [
        {
            "id": review.id,
            "rating": review.rating,
            "review": review.review,
            "customer": review.customer,
            "service": review.service,
            "product": review.product,
            "like_count": review.like_count,
            "is_liked": review.id in user_liked_reviews,
            "is_liked_by_author": review.id in product_author_liked_reviews,
            "created_at": review.created_at
        } for review in reviews
    ]