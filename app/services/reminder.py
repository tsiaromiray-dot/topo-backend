from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.reception import Reception
from app.config import settings

def check_pending_signatures(db: Session) -> list[dict]:
    """Find receptions where provisoire > 2 days without MDC signature."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.REMINDER_HOURS)
    pending = (
        db.query(Reception)
        .filter(
            Reception.date_provisoire <= cutoff,
            Reception.mdc_signee == False,
            Reception.reminder_sent == False,
        )
        .all()
    )
    results = []
    for rec in pending:
        results.append({
            "reception_id": rec.id,
            "report_id": rec.report_id,
            "type_travaux": rec.type_travaux,
            "pk": rec.pk,
            "date_provisoire": rec.date_provisoire,
        })
        rec.reminder_sent = True
    db.commit()
    return results
