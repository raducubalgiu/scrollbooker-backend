from fastapi import HTTPException, Response, Request
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse
from core.dependencies import get_user_by_token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header[7:]
            try:
                request.state.user = await get_user_by_token(token)
            except HTTPException:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid or expired token"}
                )
        else:
            request.state.user = None
        response = await call_next(request)
        return response

