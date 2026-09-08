from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User, UploadJob
from app.schemas.schemas import UploadStatus
from app.services.auth_service import get_current_user
from app.services import upload_service
from app.config import settings

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadStatus)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB upload limit.")

    job = UploadJob(user_id=current_user.id, filename=file.filename, status="validating")
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        df = upload_service.read_upload(contents, file.filename)
    except Exception as e:
        job.status = "failed"
        job.error_message = f"Could not parse file: {e}"
        db.commit()
        return UploadStatus(job_id=job.id, status=job.status, rows_processed=0, error_message=job.error_message)

    ok, messages = upload_service.validate(df)
    if not ok:
        job.status = "failed"
        job.error_message = "; ".join(messages)
        db.commit()
        return UploadStatus(job_id=job.id, status=job.status, rows_processed=0, error_message=job.error_message)

    job.status = "cleaning"
    db.commit()
    cleaned = upload_service.clean(df)

    job.status = "analyzing"
    db.commit()
    try:
        rows = upload_service.ingest(db, cleaned)
    except Exception as e:
        job.status = "failed"
        job.error_message = f"Failed to store data: {e}"
        db.commit()
        return UploadStatus(job_id=job.id, status=job.status, rows_processed=0, error_message=job.error_message)

    job.status = "complete"
    job.rows_processed = rows
    job.error_message = "; ".join(messages) if messages else None
    db.commit()

    return UploadStatus(job_id=job.id, status=job.status, rows_processed=rows, error_message=job.error_message)


@router.get("/status/{job_id}", response_model=UploadStatus)
def upload_status(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(UploadJob).filter(UploadJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Upload job not found.")
    return UploadStatus(job_id=job.id, status=job.status, rows_processed=job.rows_processed, error_message=job.error_message)
