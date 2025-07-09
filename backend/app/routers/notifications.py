from fastapi import APIRouter, Depends

from backend.app.deps import require_admin
from backend.app.notifications import run_alerts, run_retest_reminders

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/run_alerts")
def trigger_alerts(admin=Depends(require_admin)):
    run_alerts()
    return {"status": "alerts_sent"}


@router.post("/run_reminders")
def trigger_reminders(admin=Depends(require_admin)):
    run_retest_reminders()
    return {"status": "reminders_sent"}