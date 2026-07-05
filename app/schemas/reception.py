from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ReceptionCreate(BaseModel):
    tache_id: int
    type_travaux: str
    pk: Optional[str] = None
    description: Optional[str] = None

class ReceptionDefinitive(BaseModel):
    description: Optional[str] = None

class ReceptionResponse(BaseModel):
    id: int
    report_id: int
    tache_id: int
    type_travaux: str
    pk: Optional[str] = None
    description: Optional[str] = None
    date_provisoire: Optional[datetime] = None
    photos: Optional[str] = None  # JSON
    rapport_implantation: Optional[str] = None
    date_definitif: Optional[datetime] = None
    fichier_signee: Optional[str] = None
    mdc_signee: bool
    reminder_sent: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChoicesResponse(BaseModel):
    id: int
    nom: str
    is_active: int

    class Config:
        from_attributes = True

class TypeTravauxResponse(BaseModel):
    id: int
    categorie: str
    nom: str
    is_active: int

    class Config:
        from_attributes = True
