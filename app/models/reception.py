from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Reception(Base):
    __tablename__ = "receptions"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("daily_reports.id"), nullable=False)
    tache_id = Column(Integer, ForeignKey("taches.id"), nullable=False)
    type_travaux = Column(String(100), nullable=False)
    pk = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    date_provisoire = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    photos = Column(Text, nullable=True)  # JSON list of photo paths
    rapport_implantation = Column(Text, nullable=True)  # JSON list of file paths
    date_definitif = Column(DateTime, nullable=True)
    fichier_signee = Column(String(500), nullable=True)  # Path to scanned signed PDF
    mdc_signee = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    report = relationship("DailyReport")
    tache = relationship("Tache")
