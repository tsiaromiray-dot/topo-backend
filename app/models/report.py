from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    type_travaux_id = Column(Integer, ForeignKey("type_travaux.id"), nullable=False)
    type_travaux_autre = Column(String(200), nullable=True)  # if "Autres" selected
    pk_debut = Column(String(50), nullable=True)
    pk_fin = Column(String(50), nullable=True)
    pk_unique = Column(String(50), nullable=True)  # for ouvrages
    observations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="reports")
    taches = relationship("Tache", back_populates="report", cascade="all, delete-orphan")

class Tache(Base):
    __tablename__ = "taches"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("daily_reports.id"), nullable=False)
    type_tache = Column(String(50), nullable=False)  # "leve", "implantation", "reglage", "reception"
    type_implantation_id = Column(Integer, ForeignKey("type_implantations.id"), nullable=True)
    type_implantation_autre = Column(String(200), nullable=True)
    type_reglage_id = Column(Integer, ForeignKey("type_reglages.id"), nullable=True)
    type_reglage_autre = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)

    report = relationship("DailyReport", back_populates="taches")
    fichiers = relationship("Fichier", back_populates="tache", cascade="all, delete-orphan")

class Fichier(Base):
    __tablename__ = "fichiers"

    id = Column(Integer, primary_key=True, index=True)
    tache_id = Column(Integer, ForeignKey("taches.id"), nullable=False)
    nom_fichier = Column(String(255), nullable=False)
    chemin_fichier = Column(String(500), nullable=False)
    type_fichier = Column(String(50), nullable=True)  # txt, csv, dxf, pdf, jpg, png, etc.
    taille = Column(Integer, nullable=True)  # size in bytes
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tache = relationship("Tache", back_populates="fichiers")
