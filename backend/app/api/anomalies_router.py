from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User
from app.services.auth_service import get_current_user
from app.analytics import engine as A
from app.ml import anomaly_detection

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("")
def get_anomalies(
    severity: Optional[str] = Query(None, description="Filter by Low, Medium, or High"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    df = A.load_dataframe(db, exclude_cancelled=False)
    anomalies = anomaly_detection.detect_anomalies(df)
    if severity:
        anomalies = [a for a in anomalies if a["severity"].lower() == severity.lower()]

    counts = {"High": 0, "Medium": 0, "Low": 0}
    for a in anomaly_detection.detect_anomalies(df):
        counts[a["severity"]] = counts.get(a["severity"], 0) + 1

    return {"anomalies": anomalies, "counts": counts, "total": len(anomalies)}
