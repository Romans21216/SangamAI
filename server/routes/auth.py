"""Authentication routes — register (server-side with Admin SDK).

Login is handled entirely client-side via Firebase JS SDK.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from firebase_admin import auth, firestore

router = APIRouter()


class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str = ""


@router.post("/register")
async def register(req: RegisterRequest):
    """Create a new Firebase Auth user + Firestore profile document."""
    try:
        user = auth.create_user(email=req.email, password=req.password)
        db = firestore.client()
        db.collection("users").document(user.uid).set({
            "email": req.email,
            "api_key": "",
            "username": req.username,
        })
        return {"uid": user.uid, "message": "Account created successfully"}
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Email already in use")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
