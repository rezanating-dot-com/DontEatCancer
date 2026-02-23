import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ProcessingJob
from app.schemas import ProcessingJobOut

router = APIRouter(tags=["upload"])

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RIS_DIR = DATA_DIR / "ris_imports"
TEXT_DIR = DATA_DIR / "text_imports"


class TextPasteInput(BaseModel):
    text: str


@router.post("/upload/ris", response_model=ProcessingJobOut, status_code=201)
def upload_ris(file: UploadFile, db: Session = Depends(get_db)):
    """Upload a RIS file for processing."""
    RIS_DIR.mkdir(parents=True, exist_ok=True)

    dest = RIS_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Count records for the job
    from pipeline.ris_parser import parse_ris_file
    try:
        records = parse_ris_file(dest)
        total = len(records)
    except Exception:
        total = 0

    job = ProcessingJob(filename=file.filename, status="pending", total_records=total)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.post("/upload/text", response_model=ProcessingJobOut, status_code=201)
def upload_text(body: TextPasteInput, db: Session = Depends(get_db)):
    """Upload pasted text from a paper for processing."""
    TEXT_DIR.mkdir(parents=True, exist_ok=True)

    text = body.text.strip()
    if not text:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    fname = f"paste-{uuid.uuid4().hex[:8]}.txt"
    dest = TEXT_DIR / fname
    dest.write_text(text, encoding="utf-8")

    job = ProcessingJob(filename=fname, status="pending", total_records=1)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
