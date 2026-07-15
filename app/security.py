"""Authentication and request validation helpers."""

from fastapi import HTTPException, Request, WebSocket, status

from app.config import loaded_config


def extract_api_key(headers, query_params=None) -> str | None:
    """Read API key from supported locations."""
    x_api_key = headers.get("X-API-Key")
    if x_api_key:
        return x_api_key

    authorization = headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip()

    if query_params:
        return query_params.get("api_key")

    return None


def verify_api_key(api_key: str | None):
    """Validate api key when protection is enabled."""
    if not loaded_config.require_api_key:
        return

    if not loaded_config.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API key protection is enabled but api_key is not configured.",
        )

    if api_key != loaded_config.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )


def authorize_http_request(request: Request):
    """Authorize an HTTP request."""
    verify_api_key(extract_api_key(request.headers, request.query_params))


def authorize_websocket(websocket: WebSocket):
    """Authorize a websocket request."""
    verify_api_key(extract_api_key(websocket.headers, websocket.query_params))
