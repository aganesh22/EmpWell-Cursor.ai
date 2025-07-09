from __future__ import annotations

from collections import Counter
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func

from backend.app.database import get_session
from backend.app.deps import require_admin
from backend.app.models import TestTemplate, TestAttempt
from backend.app.models import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/aggregate")
def aggregate_reports(
    admin=Depends(require_admin),
    session: Session = Depends(get_session),
    by_department: bool = Query(False),
    days: int = Query(180, ge=7, le=365),
):
    """Return anonymised aggregate stats.

    Parameters
    ----------
    by_department: include per-department breakdowns
    days: timeframe for trend data (WHO-5), default 180
    """

    data: dict[str, object] = {}

    # --- WHO-5 wellbeing ---
    who_tpl = session.exec(select(TestTemplate).where(TestTemplate.key == "who5")).first()
    if who_tpl:
        overall_avg, overall_n = session.exec(
            select(func.avg(TestAttempt.normalized_score), func.count())
            .where(TestAttempt.template_id == who_tpl.id)
        ).first()

        who_dict = {"overall": {"average": round(overall_avg or 0, 2), "n": overall_n}}

        if by_department:
            rows = session.exec(
                select(User.department, func.avg(TestAttempt.normalized_score))
                .where(TestAttempt.template_id == who_tpl.id, User.id == TestAttempt.user_id)
                .group_by(User.department)
            ).all()
            who_dict["by_department"] = {
                dept or "Unknown": round(avg or 0, 2) for dept, avg in rows
            }

        # Trend (daily average over timeframe)
        since = date.today() - timedelta(days=days)
        t_rows = session.exec(
            select(func.date(TestAttempt.created_at), func.avg(TestAttempt.normalized_score))
            .where(TestAttempt.template_id == who_tpl.id, TestAttempt.created_at >= since)
            .group_by(func.date(TestAttempt.created_at))
            .order_by(func.date(TestAttempt.created_at))
        ).all()
        who_dict["trend"] = [[str(d), round(avg or 0, 2)] for d, avg in t_rows]

        data["who5"] = who_dict

    # --- MBTI ---
    mbti_tpl = session.exec(select(TestTemplate).where(TestTemplate.key == "mbti")).first()
    if mbti_tpl:
        rows = session.exec(select(TestAttempt.interpretation, User.department)
                            .where(TestAttempt.template_id == mbti_tpl.id, User.id == TestAttempt.user_id)).all()
        types_counter = Counter([r[0].split(": ")[-1] for r in rows if r[0]])
        mbti_dict = {"counts": dict(types_counter)}
        if by_department:
            dept_map: dict[str, Counter] = {}
            for interp, dept in rows:
                t = interp.split(": ")[-1]
                key = dept or "Unknown"
                dept_map.setdefault(key, Counter())[t] += 1
            mbti_dict["by_department"] = {k: dict(v) for k, v in dept_map.items()}
        data["mbti"] = mbti_dict

    # --- DISC ---
    disc_tpl = session.exec(select(TestTemplate).where(TestTemplate.key == "disc")).first()
    if disc_tpl:
        rows = session.exec(select(TestAttempt.interpretation, User.department)
                            .where(TestAttempt.template_id == disc_tpl.id, User.id == TestAttempt.user_id)).all()
        cats_counter = Counter([r[0].split(": ")[-1] for r in rows if r[0]])
        disc_dict = {"counts": dict(cats_counter)}
        if by_department:
            dept_map2: dict[str, Counter] = {}
            for interp, dept in rows:
                c = interp.split(": ")[-1]
                key = dept or "Unknown"
                dept_map2.setdefault(key, Counter())[c] += 1
            disc_dict["by_department"] = {k: dict(v) for k, v in dept_map2.items()}
        data["disc"] = disc_dict

    return data