from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from backend.core.database import async_engine
from backend.core.dependencies import UserSession
from backend.core.middlewares.cors_middleware import CORSCustomMiddleware
from backend.models import Base
from backend.api.v1.endpoints.user import user, role, permission, consent, notification, user_currency
from backend.api.v1.endpoints.auth import auth
from backend.api.v1.endpoints.social import follow, hashtag, post
from backend.api.v1.endpoints.booking import business, product, appointment, schedule, review, employment_request
from backend.api.v1.endpoints.booking.nomenclature import business_domain, business_type, service, filter, sub_filter, service_domain, profession, currency
from backend.core.middlewares.auth_middleware import AuthMiddleware
from backend.core.exceptions import global_exception_handler, http_exception_handler, validation_exception_handler
from backend.core.scheduler import start as start_scheduler, scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)

app = FastAPI(lifespan=lifespan, root_path="/api/v1")

app.add_middleware(AuthMiddleware) #type: ignore
app.add_middleware(CORSCustomMiddleware) #type: ignore

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler) #type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler) #type: ignore

# Auth
app.include_router(auth.router)

# User
app.include_router(user.router, dependencies=[UserSession])
app.include_router(role.router, dependencies=[UserSession])
app.include_router(permission.router, dependencies=[UserSession])
app.include_router(consent.router, dependencies=[UserSession])
app.include_router(notification.router, dependencies=[UserSession])
app.include_router(user_currency.router, dependencies=[UserSession])

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

# Social
app.include_router(follow.router, dependencies=[UserSession])
app.include_router(hashtag.router, dependencies=[UserSession])
app.include_router(post.router, dependencies=[UserSession])

