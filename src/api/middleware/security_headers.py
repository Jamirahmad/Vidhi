"""
Security Headers Middleware

Adds baseline HTTP response headers recommended for production deployments.
"""

from fastapi import Request


async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)

    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

    # HSTS should be enabled only behind HTTPS in production.
    host = request.url.scheme
    if host == "https":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

    return response
