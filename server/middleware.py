"""Authentication dependency for FastAPI routes."""

from fastapi import HTTPException, Request
from firebase_admin import auth


async def get_current_user(request: Request) -> str:
    """Extract & verify Firebase ID token → return uid.

    Usage in routes::

        @router.get("/protected")
        async def protected(user_id: str = Depends(get_current_user)):
            ...
    """
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        token = header.split("Bearer ", 1)[1]
    else:
        # Fallback: accept token as query param (for iframe/embed use)
        token = request.query_params.get("token", "")
    
    if not token:
        raise HTTPException(status_code=401, detail="Missing or invalid authorization")
    try:
        decoded = auth.verify_id_token(token)
        return decoded["uid"]
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
