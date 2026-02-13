"""Upload routes — PDF, YouTube, CSV ingestion pipelines."""

import os
import io
import tempfile

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
import pandas as pd

from middleware import get_current_user
from modules.rag import (
    load_and_split_pdf,
    create_vectorstore,
    process_youtube,
    extract_video_id,
)
from modules.database import save_vectorstore_to_firestore, save_dataframe_to_firestore

router = APIRouter()


# ── PDF ───────────────────────────────────────────────────────────────

@router.post("/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    """Upload a PDF → chunk → embed → save vectorstore to Firestore."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        splits = load_and_split_pdf(tmp_path)
        vectorstore = create_vectorstore(splits)
        save_vectorstore_to_firestore(user_id, file.filename, vectorstore, content_type="pdf")

        # Save raw PDF bytes for later viewing
        from modules.database import save_pdf_bytes
        save_pdf_bytes(user_id, file.filename, content)

        os.unlink(tmp_path)
        return {"message": f"{file.filename} indexed and saved", "file_name": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── YouTube ───────────────────────────────────────────────────────────

class YouTubeRequest(BaseModel):
    url: str


@router.post("/youtube")
async def upload_youtube(
    req: YouTubeRequest,
    user_id: str = Depends(get_current_user),
):
    """Extract YouTube transcript → chunk → embed → save."""
    try:
        video_id = extract_video_id(req.url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        vectorstore, transcript = process_youtube(req.url)
        file_name = f"youtube_{video_id}"
        save_vectorstore_to_firestore(user_id, file_name, vectorstore, content_type="youtube")

        return {"message": f"Video {video_id} transcript indexed", "file_name": file_name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── CSV ───────────────────────────────────────────────────────────────

@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    """Upload a CSV → save DataFrame to Firestore."""
    try:
        raw = await file.read()
        df = pd.read_csv(io.BytesIO(raw))

        save_dataframe_to_firestore(user_id, file.filename, df)

        return {
            "message": f"{file.filename} uploaded",
            "file_name": file.filename,
            "shape": list(df.shape),
            "columns": list(df.columns),
            "preview": df.head(10).to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
