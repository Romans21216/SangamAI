import streamlit as st
from firebase_admin import auth, firestore
import requests

API_KEY = "PUT_YOUR_OWN_API_KEY_HERE_WHY_TAKE_MINE"


def verify_password(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    r = requests.post(url, json=payload)
    if "error" in r.json():
        return None
    else:
        return r.json()["localId"]

def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        # Create user profile in Firestore
        db = firestore.client()
        db.collection("users").document(user.uid).set({
            "email": email,
            "api_key": "",
            "username": "",
        })
        return user.uid
    except Exception as e:
        st.error(f"Error: {e}")
        return None


# ── Username helpers ──────────────────────────────────────────────────

def get_username(user_id: str) -> str:
    """Return the stored username, or empty string if not set."""
    db = firestore.client()
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        return doc.to_dict().get("username", "")
    return ""


def set_username(user_id: str, username: str) -> None:
    """Persist *username* to the user's Firestore document."""
    db = firestore.client()
    db.collection("users").document(user_id).update({"username": username})


def login_user(email):
    try:
        user = auth.get_user_by_email(email)
        return user.uid
    except:
        return None
    
