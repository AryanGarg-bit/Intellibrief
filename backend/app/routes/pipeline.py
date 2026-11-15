"""Protected internal scheduler endpoint for daily runs."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from app.config import settings
from app.jobs.daily_pipeline import run_daily_pipeline

router = APIRouter(prefix="/internal/jobs", tags=["Internal Pipeline Jobs"])


class DailyRunRequest(BaseModel):
    report_date: Optional[str] = None


@router.post("/daily")
def trigger_daily_job(
    req: Optional[DailyRunRequest] = None,
    x_job_secret: Optional[str] = Header(None, alias="X-Job-Secret"),
) -> Dict[str, Any]:
    """
    Trigger the daily pipeline.
    Secured by X-Job-Secret header.
    """
    if x_job_secret != settings.internal_job_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal job secret",
        )

    date_str = req.report_date if req else None
    result = run_daily_pipeline(report_date=date_str)
    return {"status": "success", "result": result}
