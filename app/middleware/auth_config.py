"""
Configuration and utilities for applying authentication middleware to specific routes.
"""
from typing import List
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.security import verify_token


def configure_protected_routes(app: FastAPI, protected_prefixes: List[str] = None):
    """
    Configure which route prefixes require authentication.
    
    Args:
        app: FastAPI application instance
        protected_prefixes: List of route prefixes that require authentication
                          Default: ["/chat", "/workspace", "/documents"]
    """
    if protected_prefixes is None:
        protected_prefixes = ["/chat", "/workspace", "/documents"]
    
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        """
        Middleware to check authentication for protected routes.
        """
        # Public routes that don't require authentication
        public_routes = [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/signup",
            "/auth/login",
            "/auth/token",
        ]
        
        # Check if route is public
        path = request.url.path
        is_public = (
            path in public_routes or
            path.startswith("/docs") or
            path.startswith("/redoc") or
            path.startswith("/openapi.json") or
            path.startswith("/static")
        )
        
        # Check if route is protected
        is_protected = any(path.startswith(prefix) for prefix in protected_prefixes)
        
        # If route is not protected or is public, skip auth
        if not is_protected or is_public:
            return await call_next(request)
        
        # Get and verify token
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing authentication token"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            # Extract token
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
            
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
            
            # Continue to endpoint
            response = await call_next(request)
            return response
        
        except ValueError as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e)},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Authentication error"},
            )


def get_current_user_from_request(request: Request) -> dict:
    """
    Extract current user information from request state.
    
    This is useful in endpoints that use the auth middleware.
    
    Args:
        request: FastAPI Request object
    
    Returns:
        Dict with user_id and user_email
    
    Raises:
        HTTPException: If user info not found in request state
    """
    user_id = getattr(request.state, "user_id", None)
    user_email = getattr(request.state, "user_email", None)
    
    if not user_id or not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    
    return {
        "user_id": user_id,
        "user_email": user_email
    }
