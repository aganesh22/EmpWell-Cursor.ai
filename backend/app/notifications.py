import os
import smtplib
from email.message import EmailMessage
from sqlmodel import Session, select
from datetime import date, timedelta

from backend.app.database import engine
from backend.app.models import TestTemplate, TestAttempt, User

SMTP_HOST = os.getenv("EMAIL_HOST")
SMTP_PORT = int(os.getenv("EMAIL_PORT", "587"))
SMTP_USER = os.getenv("EMAIL_USER")
SMTP_PASS = os.getenv("EMAIL_PASS")
HR_EMAIL = os.getenv("HR_ALERT_EMAIL")


def _send_email(subject: str, body: str, to: str):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        return  # email not configured
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to
    msg.set_content(body)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


LOW_WELLBEING_THRESHOLD = 50  # percent


def run_alerts(days: int = 1):
    """Send HR alerts if any user scored below threshold in past `days`."""
    if not HR_EMAIL:
        return
    with Session(engine) as session:
        who_tpl = session.exec(select(TestTemplate).where(TestTemplate.key == "who5")).first()
        if not who_tpl:
            return
        since = date.today() - timedelta(days=days)
        low_attempts = session.exec(
            select(TestAttempt, User)
            .where(
                TestAttempt.template_id == who_tpl.id,
                TestAttempt.created_at >= since,
                TestAttempt.normalized_score < LOW_WELLBEING_THRESHOLD,
                User.id == TestAttempt.user_id,
            )
        ).all()
        if not low_attempts:
            return
        body_lines = ["Employees with low wellbeing scores:"]
        for attempt, user in low_attempts:
            body_lines.append(f"- {user.full_name or user.email} | Score: {attempt.normalized_score:.1f}")
        _send_email("Wellbeing Alert", "\n".join(body_lines), HR_EMAIL)


def run_retest_reminders(days_since: int = 90):
    """Send retest reminders to users who haven't taken WHO-5 in `days_since`."""
    if not SMTP_USER:
        return
    with Session(engine) as session:
        who_tpl = session.exec(select(TestTemplate).where(TestTemplate.key == "who5")).first()
        if not who_tpl:
            return
        cutoff = date.today() - timedelta(days=days_since)
        # Users whose latest attempt < cutoff
        users = session.exec(select(User)).all()
        for user in users:
            last = session.exec(
                select(TestAttempt)
                .where(TestAttempt.template_id == who_tpl.id, TestAttempt.user_id == user.id)
                .order_by(TestAttempt.created_at.desc())
            ).first()
            if not last or last.created_at.date() <= cutoff:
                _send_email(
                    "Time for your wellbeing check-in",
                    "Hi, please take 2 minutes to complete your WHO-5 wellbeing check.",
                    user.email,
                )