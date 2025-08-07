import re
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.exceptions import BadRequestError
from starlette.requests import Request

class InputSanitizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check for potential SQL injection patterns
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            if body:
                body_str = body.decode()
                dangerous_patterns = [
                    r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
                    r"(script|javascript|vbscript)",
                    r"(<|>|&lt;|&gt;)"
                ]
                
                for pattern in dangerous_patterns:
                    if re.search(pattern, body_str, re.IGNORECASE):
                        raise BadRequestError("Invalid input detected")
        
        return await call_next(request)