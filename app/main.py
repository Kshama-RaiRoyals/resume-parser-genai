"""FastAPI application exposing resume upload and retrieval endpoints."""
from contextlib import asynccontextmanager
from uuid import uuid4
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.models import UploadResponse, ResumeData
from app.services.parser import extract_text, ResumeParseError, MAX_FILE_BYTES
from app.services.llm_service import extract_resume_data
from app.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)
# In-memory store is suitable for this take-home demo only.
RESUME_STORE: dict[str, UploadResponse] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Resume Parser API starting")
    yield
    logger.info("Resume Parser API shutting down")


app = FastAPI(
    title="Resume Parser API",
    description="Upload a PDF/DOCX resume and retrieve LLM-extracted structured information.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Basic liveness check."""
    return {"status": "ok"}


@app.post("/api/upload", response_model=UploadResponse, status_code=201)
async def upload_resume(file: UploadFile = File(...)) -> UploadResponse:
    """Upload and parse one PDF/DOCX resume."""
    filename = file.filename or "uploaded_file"
    suffix = Path(filename).suffix.lower()
    if suffix not in {".pdf", ".docx"}:
        raise HTTPException(status_code=415, detail="Unsupported file type. Upload a PDF or DOCX file.")
    content = await file.read()
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 10 MB upload limit.")
    try:
        resume_text = extract_text(filename, content)
        data, mode = extract_resume_data(resume_text)
    except ResumeParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("Resume extraction configuration or LLM error")
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected resume processing error")
        raise HTTPException(status_code=502, detail="Resume processing failed. Please retry.") from exc

    document_id = str(uuid4())
    result = UploadResponse(
        document_id=document_id,
        filename=filename,
        extracted_data=data,
        mode=mode,
    )
    RESUME_STORE[document_id] = result
    logger.info("Resume processed: document_id=%s filename=%s mode=%s", document_id, filename, mode)
    return result


@app.get("/api/resume/{document_id}", response_model=UploadResponse)
def get_resume(document_id: str) -> UploadResponse:
    """Retrieve a previously extracted resume."""
    result = RESUME_STORE.get(document_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Resume not found for the supplied document_id.")
    return result
