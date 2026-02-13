"""Profile routes — read & update user profile fields."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from firebase_admin import firestore

from middleware import get_current_user

router = APIRouter()


@router.get("/")
async def get_profile(user_id: str = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    db = firestore.client()
    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User profile not found")

    data = doc.to_dict()
    return {
        "uid": user_id,
        "email": data.get("email", ""),
        "username": data.get("username", ""),
        "has_api_key": bool(data.get("api_key")),
        "api_key_hint": f"...{data['api_key'][-8:]}" if data.get("api_key") else None,
    }


class UpdateUsername(BaseModel):
    username: str


@router.put("/username")
async def update_username(body: UpdateUsername, user_id: str = Depends(get_current_user)):
    """Update the display name."""
    db = firestore.client()
    db.collection("users").document(user_id).update({"username": body.username.strip()})
    return {"message": "Username updated"}


class UpdateApiKey(BaseModel):
    api_key: str


@router.put("/api-key")
async def update_api_key(body: UpdateApiKey, user_id: str = Depends(get_current_user)):
    """Update the stored OpenRouter API key."""
    db = firestore.client()
    db.collection("users").document(user_id).update({"api_key": body.api_key})
    return {"message": "API key updated"}


@router.get("/api-key")
async def get_api_key(user_id: str = Depends(get_current_user)):
    """Return the stored API key (for use in chat requests)."""
    db = firestore.client()
    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        return {"api_key": ""}
    return {"api_key": doc.to_dict().get("api_key", "")}
