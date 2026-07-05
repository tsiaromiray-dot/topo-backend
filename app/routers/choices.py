from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.choices import TypeTravaux, TypeImplantation, TypeReglage
from app.models.report import Fichier
from app.schemas.reception import TypeTravauxResponse, ChoicesResponse
from app.routers.auth import require_admin, get_current_user
from app.models.user import User

router = APIRouter(prefix="/choices", tags=["choices"])

# --- Type Travaux ---
@router.get("/travaux", response_model=List[TypeTravauxResponse])
def list_travaux(db: Session = Depends(get_db)):
    return db.query(TypeTravaux).filter(TypeTravaux.is_active == 1).all()

@router.post("/travaux")
def create_travaux(categorie: str, nom: str, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    t = TypeTravaux(categorie=categorie, nom=nom)
    db.add(t)
    db.commit()
    return {"message": "Type de travaux ajouté", "id": t.id}

@router.delete("/travaux/{id}")
def delete_travaux(id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    t = db.query(TypeTravaux).filter(TypeTravaux.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Type non trouvé")
    t.is_active = 0
    db.commit()
    return {"message": "Type désactivé"}

# --- Type Implantations ---
@router.get("/implantations", response_model=List[ChoicesResponse])
def list_implantations(db: Session = Depends(get_db)):
    return db.query(TypeImplantation).filter(TypeImplantation.is_active == 1).all()

@router.post("/implantations")
def create_implantation(nom: str, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    t = TypeImplantation(nom=nom)
    db.add(t)
    db.commit()
    return {"message": "Type d'implantation ajouté", "id": t.id}

@router.delete("/implantations/{id}")
def delete_implantation(id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    t = db.query(TypeImplantation).filter(TypeImplantation.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Type non trouvé")
    t.is_active = 0
    db.commit()
    return {"message": "Type désactivé"}

# --- Type Réglages ---
@router.get("/reglages", response_model=List[ChoicesResponse])
def list_reglages(db: Session = Depends(get_db)):
    return db.query(TypeReglage).filter(TypeReglage.is_active == 1).all()

@router.post("/reglages")
def create_reglage(nom: str, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    t = TypeReglage(nom=nom)
    db.add(t)
    db.commit()
    return {"message": "Type de réglage ajouté", "id": t.id}

@router.delete("/reglages/{id}")
def delete_reglage(id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    t = db.query(TypeReglage).filter(TypeReglage.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Type non trouvé")
    t.is_active = 0
    db.commit()
    return {"message": "Type désactivé"}
