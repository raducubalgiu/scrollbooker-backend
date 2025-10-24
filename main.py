import httpx
from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.database import async_engine
from core.dependencies import UserSession
from core.middlewares.cors_middleware import CORSCustomMiddleware
from models import Base
from api.v1.endpoints.search import search
from api.v1.endpoints.user import user, role, permission, consent, notification
from api.v1.endpoints.auth import auth
from api.v1.endpoints.onboarding import onboarding
from api.v1.endpoints.social import follow, hashtag, post, bookmark_posts,repost, like, comment
from api.v1.endpoints.booking import business, product, appointment, schedule, review, employment_request
from api.v1.endpoints.nomenclature import business_domain, business_type, service, filter, sub_filter, service_domain, profession, currency, problem
from api.v1.endpoints.integration import google
from core.middlewares.auth_middleware import AuthMiddleware
from core.exceptions import register_exception_handler
from core.scheduler import start as start_scheduler, scheduler
from core import http_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Scheduler
    start_scheduler()

    # HTTPX Client
    http_client.async_client = httpx.AsyncClient(
        timeout=httpx.Timeout(5.0, read=5.0, connect=3.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        headers={"Accept": "application/json"}
    )
    try:
        yield
    finally:
        if http_client.async_client is not None:
            await http_client.async_client.aclose()
            http_client.async_client = None
        scheduler.shutdown(wait=False)

app = FastAPI(lifespan=lifespan, root_path="/api/v1")

app.add_middleware(AuthMiddleware) #type: ignore
app.add_middleware(CORSCustomMiddleware) #type: ignore

# Error exception handler
register_exception_handler(app)

# Auth
app.include_router(auth.router)

# OnBoarding
app.include_router(onboarding.router, dependencies=[UserSession])

# Upload media
#app.include_router(upload_media.router, dependencies=[UserSession])

# User
app.include_router(user.router, dependencies=[UserSession])
app.include_router(role.router)
app.include_router(permission.router, dependencies=[UserSession])
app.include_router(consent.router, dependencies=[UserSession])
app.include_router(notification.router, dependencies=[UserSession])

# Search
app.include_router(search.router, dependencies=[UserSession])

# Booking
app.include_router(currency.router, dependencies=[UserSession])
app.include_router(business_domain.router, dependencies=[UserSession])
app.include_router(business_type.router, dependencies=[UserSession])
app.include_router(profession.router, dependencies=[UserSession])
app.include_router(filter.router, dependencies=[UserSession])
app.include_router(sub_filter.router, dependencies=[UserSession])
app.include_router(service.router, dependencies=[UserSession])
app.include_router(service_domain.router, dependencies=[UserSession])
app.include_router(business.router, dependencies=[UserSession])
app.include_router(product.router, dependencies=[UserSession])
app.include_router(appointment.router, dependencies=[UserSession])
app.include_router(schedule.router, dependencies=[UserSession])
app.include_router(review.router, dependencies=[UserSession])
app.include_router(employment_request.router, dependencies=[UserSession])
app.include_router(problem.router, dependencies=[UserSession])

# Social
app.include_router(like.router, dependencies=[UserSession])
app.include_router(comment.router, dependencies=[UserSession])
app.include_router(follow.router, dependencies=[UserSession])
app.include_router(repost.router, dependencies=[UserSession])
app.include_router(hashtag.router, dependencies=[UserSession])
app.include_router(post.router, dependencies=[UserSession])
app.include_router(bookmark_posts.router, dependencies=[UserSession])

# Integration
app.include_router(google.router, dependencies=[UserSession])

