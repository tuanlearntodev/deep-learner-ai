"""
Authentication and logging middleware for the application.
"""
import time
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.security import verify_token
from app.services.auth_service import get_user_by_email
from app.services.dependencies import get_db


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle JWT authentication for protected routes.
    """
    
    # Routes that don't require authentication
    PUBLIC_ROUTES = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/auth/signup",
        "/auth/login",
        "/auth/token",
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request and verify authentication if needed.
        """
        # Skip authentication for public routes
        if self._is_public_route(request.url.path):
            return await call_next(request)
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if it's a Bearer token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header format. Expected 'Bearer <token>'"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = parts[1]
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Attach user info to request state
        request.state.user_email = payload.get("sub")
        request.state.user_id = payload.get("user_id")
        
        # Continue to the endpoint
        response = await call_next(request)
        return response
    
    def _is_public_route(self, path: str) -> bool:
        """Check if the route is public."""
        # Exact match
        if path in self.PUBLIC_ROUTES:
            return True
        
        # Prefix match for static files and docs
        public_prefixes = ["/docs", "/redoc", "/openapi.json", "/static"]
        return any(path.startswith(prefix) for prefix in public_prefixes)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and their response times.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request details and timing.
        """
        start_time = time.time()
        
        # Log request
        print(f"📨 {request.method} {request.url.path}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Add custom header with processing time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            status_emoji = "✅" if response.status_code < 400 else "❌"
            print(f"{status_emoji} {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
            
            return response
        
        except Exception as e:
            process_time = time.time() - start_time
            print(f"❌ {request.method} {request.url.path} - ERROR - {process_time:.3f}s - {str(e)}")
            raise


class CORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware (use FastAPI's CORSMiddleware in production).
    """
    
    def __init__(self, app, allow_origins=None, allow_methods=None, allow_headers=None):
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["*"]
        self.allow_headers = allow_headers or ["*"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add CORS headers to responses.
        """
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = ", ".join(self.allow_origins)
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
            response.headers["Access-Control-Max-Age"] = "3600"
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = ", ".join(self.allow_origins)
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware.
    """
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # In production, use Redis for distributed rate limiting
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check rate limit before processing request.
        """
        # Get client identifier (IP address or user ID)
        client_id = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/"]:
            return await call_next(request)
        
        current_time = time.time()
        
        # Initialize or clean up old requests
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove requests outside the time window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if current_time - req_time < self.window_seconds
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_id]) >= self.max_requests:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds} seconds."
                }
            )
        
        # Add current request
        self.requests[client_id].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(self.max_requests - len(self.requests[client_id]))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Catch and handle all unhandled exceptions.
        """
        try:
            response = await call_next(request)
            return response
        
        except HTTPException:
            # Let FastAPI handle HTTP exceptions
            raise
        
        except Exception as e:
            # Log the error
            print(f"💥 Unhandled exception: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return a generic error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error",
                    "error": str(e) if request.app.debug else "An unexpected error occurred"
                }
            )
