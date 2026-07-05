from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FichierResponse(BaseModel):
    id: int
    nom_fichier: str
    chemin_fichier: str
    type_fichier: Optional[str] = None
    taille: Optional[int] = None
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TacheCreate(BaseModel):
    type_tache: str  # leve, implantation, reglage, reception
    type_implantation_id: Optional[int] = None
    type_implantation_autre: Optional[str] = None
    type_reglage_id: Optional[int] = None
    type_reglage_autre: Optional[str] = None
    description: Optional[str] = None

class TacheResponse(BaseModel):
    id: int
    report_id: int
    type_tache: str
    type_implantation_id: Optional[int] = None
    type_implantation_autre: Optional[str] = None
    type_reglage_id: Optional[int] = None
    type_reglage_autre: Optional[str] = None
    description: Optional[str] = None
    fichiers: List[FichierResponse] = []

    class Config:
        from_attributes = True

class DailyReportCreate(BaseModel):
    type_travaux_id: int
    type_travaux_autre: Optional[str] = None
    pk_debut: Optional[str] = None
    pk_fin: Optional[str] = None
    pk_unique: Optional[str] = None
    observations: Optional[str] = None
    taches: List[TacheCreate] = []

class DailyReportResponse(BaseModel):
    id: int
    user_id: int
    date: Optional[datetime] = None
    type_travaux_id: int
    type_travaux_autre: Optional[str] = None
    pk_debut: Optional[str] = None
    pk_fin: Optional[str] = None
    pk_unique: Optional[str] = None
    observations: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    taches: List[TacheResponse] = []
    user_name: Optional[str] = None

    class Config:
        from_attributes = True
