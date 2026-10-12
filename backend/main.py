import os
import uuid
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io

from file_processor import FileProcessor
from detector import AIDetector
from humanizer import TextHumanizer

app = FastAPI(
    title="StealthDoc API",
    description="Local AI Text Detector & Humanizer Backend Engine",
    version="1.0.0"
)

# Enable CORS for local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory document session cache (session_id -> data)
sessions: Dict[str, Dict[str, Any]] = {}

detector = AIDetector()
humanizer = TextHumanizer()

class DetectRequest(BaseModel):
    text: str

class HumanizeRequest(BaseModel):
    session_id: Optional[str] = None
    text: Optional[str] = None
    api_key: Optional[str] = None

@app.get("/api/health")
def health_check():
    """Health and model capability check."""
    return {
        "status": "online",
        "service": "StealthDoc AI Detector & Humanizer",
        "has_gemini_key": bool(os.getenv("GEMINI_API_KEY")),
        "detector_model": detector.model_name
    }

@app.post("/api/detect")
def detect_endpoint(payload: DetectRequest):
    """Analyzes raw text and returns AI %, Human %, and Mixed % scores."""
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    results = detector.detect_text(payload.text)
    return results

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts .docx or .txt file upload, extracts paragraphs, and runs baseline AI detection.
    """
    filename = file.filename or "document.txt"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".docx", ".txt"]:
        raise HTTPException(status_code=400, detail="Only .docx and .txt files are supported.")

    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if ext == ".docx":
        full_text, paragraphs = FileProcessor.extract_from_docx(content_bytes)
    else:
        full_text, paragraphs = FileProcessor.extract_from_txt(content_bytes)

    session_id = str(uuid.uuid4())
    baseline_stats = detector.detect_text(full_text)

    sessions[session_id] = {
        "filename": filename,
        "extension": ext,
        "original_bytes": content_bytes,
        "paragraphs": paragraphs,
        "full_text": full_text,
        "baseline_stats": baseline_stats,
        "humanized_paragraphs": None,
        "humanized_stats": None
    }

    return {
        "session_id": session_id,
        "filename": filename,
        "total_paragraphs": len(paragraphs),
        "total_words": len(full_text.split()),
        "full_text": full_text,
        "paragraphs": paragraphs,
        "baseline_stats": baseline_stats
    }

@app.post("/api/humanize")
def humanize_endpoint(
    payload: HumanizeRequest,
    x_gemini_api_key: Optional[str] = Header(None)
):
    """
    Rewrites text using Gemini API with burstiness/perplexity tuning,
    calculates post-humanization stats, and updates session.
    """
    api_key = payload.api_key or x_gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Gemini API key is required. Supply via GEMINI_API_KEY env var, request body, or X-Gemini-Api-Key header."
        )

    # Path 1: Session-based document humanization
    if payload.session_id and payload.session_id in sessions:
        session = sessions[payload.session_id]
        paragraphs = session["paragraphs"]

        humanized_paragraphs = humanizer.humanize_document(paragraphs, api_key=api_key)
        humanized_full_text = "\n\n".join(p.get("text", "") for p in humanized_paragraphs if p.get("text", "").strip())
        
        post_stats = detector.detect_text(humanized_full_text)

        session["humanized_paragraphs"] = humanized_paragraphs
        session["humanized_full_text"] = humanized_full_text
        session["humanized_stats"] = post_stats

        return {
            "session_id": payload.session_id,
            "before_stats": session["baseline_stats"],
            "after_stats": post_stats,
            "humanized_full_text": humanized_full_text,
            "humanized_paragraphs": humanized_paragraphs
        }

    # Path 2: Direct raw text humanization
    if payload.text and payload.text.strip():
        rewritten_text = humanizer.humanize_paragraph(payload.text, api_key=api_key)
        before_stats = detector.detect_text(payload.text)
        after_stats = detector.detect_text(rewritten_text)

        return {
            "session_id": None,
            "before_stats": before_stats,
            "after_stats": after_stats,
            "humanized_full_text": rewritten_text,
            "humanized_paragraphs": [{"id": 0, "text": rewritten_text}]
        }

    raise HTTPException(status_code=400, detail="Either a valid session_id or text must be provided.")

@app.get("/api/download/{session_id}")
def download_file(session_id: str):
    """
    Reconstructs the humanized document back into .docx or .txt format,
    preserving original styles and formatting.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    session = sessions[session_id]
    ext = session["extension"]
    filename = session["filename"]
    base_name = os.path.splitext(filename)[0]
    out_filename = f"{base_name}_humanized{ext}"

    humanized_paragraphs = session.get("humanized_paragraphs") or session["paragraphs"]

    if ext == ".docx":
        out_bytes = FileProcessor.reconstruct_docx(session["original_bytes"], humanized_paragraphs)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        out_bytes = FileProcessor.reconstruct_txt(humanized_paragraphs)
        media_type = "text/plain; charset=utf-8"

    return StreamingResponse(
        io.BytesIO(out_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{out_filename}"'}
    )
