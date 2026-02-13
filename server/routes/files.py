"""File management routes — list and delete user files."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from firebase_admin import firestore

from middleware import get_current_user
from modules.database import load_pdf_bytes

router = APIRouter()


@router.get("/")
async def list_files(user_id: str = Depends(get_current_user)):
    """Return all files (PDF, YouTube, CSV) for the authenticated user."""
    db = firestore.client()
    files_ref = db.collection("users").document(user_id).collection("files")

    files = []
    for doc in files_ref.stream():
        data = doc.to_dict()
        files.append({
            "file_name": doc.id,
            "content_type": data.get("content_type", "pdf"),
            "created_at": str(data.get("created_at", "")),
        })

    return {"files": files}


@router.delete("/{file_name}")
async def delete_file(file_name: str, user_id: str = Depends(get_current_user)):
    """Delete a file and all its sub-collections (chunks, messages)."""
    db = firestore.client()
    doc_ref = db.collection("users").document(user_id).collection("files").document(file_name)

    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete sub-collections
    for sub in ("chunks", "messages", "pdf_raw"):
        for child in doc_ref.collection(sub).stream():
            child.reference.delete()

    doc_ref.delete()

    # Invalidate vectorstore cache
    from routes.chat import _invalidate_cache
    _invalidate_cache(user_id, file_name)

    return {"message": f"{file_name} deleted"}


@router.get("/{file_name}/pdf")
async def get_pdf(file_name: str, user_id: str = Depends(get_current_user)):
    """Return the raw PDF file for in-browser viewing."""
    pdf_bytes = load_pdf_bytes(user_id, file_name)
    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="PDF not found")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{file_name}"'},
    )
