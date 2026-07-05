from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User, RoleEnum
from app.models.report import DailyReport, Tache, Fichier
from app.models.reception import Reception
from app.schemas.reception import ReceptionCreate, ReceptionResponse
from app.routers.auth import get_current_user, require_admin
from app.utils.file_handler import save_upload_file
from app.services.reminder import check_pending_signatures
import json
from datetime import datetime, timezone

router = APIRouter(prefix="/receptions", tags=["receptions"])

@router.post("/", response_model=ReceptionResponse)
def create_reception(
    tache_id: int = Form(...),
    type_travaux: str = Form(...),
    pk: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tache = db.query(Tache).filter(Tache.id == tache_id).first()
    if not tache:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")

    reception = Reception(
        report_id=tache.report_id,
        tache_id=tache_id,
        type_travaux=type_travaux,
        pk=pk,
        description=description,
    )
    db.add(reception)
    db.commit()
    db.refresh(reception)
    return reception

@router.post("/{reception_id}/photos")
def upload_photos(
    reception_id: int,
    files: List[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reception = db.query(Reception).filter(Reception.id == reception_id).first()
    if not reception:
        raise HTTPException(status_code=404, detail="Réception non trouvée")

    paths = []
    for f in files:
        path = save_upload_file(f, subdir=f"receptions/{reception_id}/photos")
        paths.append(path)

    existing = json.loads(reception.photos) if reception.photos else []
    existing.extend(paths)
    reception.photos = json.dumps(existing)
    db.commit()
    return {"photos": paths}

@router.post("/{reception_id}/rapport-implantation")
def upload_rapport_implantation(
    reception_id: int,
    files: List[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reception = db.query(Reception).filter(Reception.id == reception_id).first()
    if not reception:
        raise HTTPException(status_code=404, detail="Réception non trouvée")

    paths = []
    for f in files:
        path = save_upload_file(f, subdir=f"receptions/{reception_id}/rapports")
        paths.append(path)

    existing = json.loads(reception.rapport_implantation) if reception.rapport_implantation else []
    existing.extend(paths)
    reception.rapport_implantation = json.dumps(existing)
    db.commit()
    return {"rapports": paths}

@router.post("/{reception_id}/signer-mdc")
def signer_mdc(
    reception_id: int,
    file: UploadFile = File(...),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    reception = db.query(Reception).filter(Reception.id == reception_id).first()
    if not reception:
        raise HTTPException(status_code=404, detail="Réception non trouvée")

    path = save_upload_file(file, subdir=f"receptions/{reception_id}/signe")
    reception.fichier_signee = path
    reception.mdc_signee = True
    reception.date_definitif = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Fichier signé MDC enregistré"}

@router.get("/", response_model=List[ReceptionResponse])
def list_receptions(
    search: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Reception)

    if user.role != RoleEnum.super_admin.value:
        if user.role == RoleEnum.chef_equipe.value:
            member_ids = [m.id for m in db.query(User).filter(User.chef_equipe_id == user.id).all()]
            sub = db.query(DailyReport.id).filter(
                DailyReport.user_id.in_([user.id] + member_ids)
            ).subquery()
            query = query.filter(Reception.report_id.in_(sub))
        else:
            sub = db.query(DailyReport.id).filter(DailyReport.user_id == user.id).subquery()
            query = query.filter(Reception.report_id.in_(sub))

    if search:
        query = query.filter(
            (Reception.type_travaux.ilike(f"%{search}%")) |
            (Reception.pk.ilike(f"%{search}%")) |
            (Reception.description.ilike(f"%{search}%"))
        )

    return query.order_by(Reception.date_provisoire.desc()).all()

@router.get("/pending-mdc")
def pending_mdc(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    pending = check_pending_signatures(db)
    return {"pending": pending}
