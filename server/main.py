import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

load_dotenv()


def _init_firebase() -> None:
    """Initialize Firebase Admin SDK (idempotent)."""
    try:
        firebase_admin.get_app()
    except ValueError:
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT", "serviceAccount.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
        else:
            # For deployment: JSON content in env variable
            raw = os.getenv("FIREBASE_CREDENTIALS", "{}")
            cred_data = json.loads(raw)
            cred_data["private_key"] = cred_data["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(cred_data)
        firebase_admin.initialize_app(cred)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    _init_firebase()
    # Pre-warm embeddings model in background
    from modules.rag import get_embeddings
    get_embeddings()
    yield


app = FastAPI(title="SangamAI API", version="1.0.0", lifespan=lifespan)

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────
from routes.auth import router as auth_router        # noqa: E402
from routes.upload import router as upload_router    # noqa: E402
from routes.chat import router as chat_router        # noqa: E402
from routes.files import router as files_router      # noqa: E402
from routes.profile import router as profile_router  # noqa: E402

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(upload_router, prefix="/api/upload", tags=["upload"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(files_router, prefix="/api/files", tags=["files"])
app.include_router(profile_router, prefix="/api/profile", tags=["profile"])


# ── Utility endpoints ─────────────────────────────────────────────────

MODEL_OPTIONS = [
    "google/gemini-2.5-flash",
    "google/gemini-3-flash-preview",
    "anthropic/claude-sonnet-4.5",
    "anthropic/claude-3.7-sonnet",
    "openai/gpt-5.2",
    "openai/gpt-4o-mini",
    "x-ai/grok-4.1-fast",
    "x-ai/grok-4-fast",
]


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/models")
async def list_models():
    return {"models": MODEL_OPTIONS}
