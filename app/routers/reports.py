from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User, RoleEnum
from app.models.report import DailyReport, Tache, Fichier
from app.models.reception import Reception
from app.schemas.report import DailyReportCreate, DailyReportResponse, TacheResponse, FichierResponse
from app.routers.auth import get_current_user, require_admin
from app.utils.file_handler import save_upload_file
import json

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/", response_model=DailyReportResponse)
def create_report(
    type_travaux_id: int = Form(...),
    type_travaux_autre: Optional[str] = Form(None),
    pk_debut: Optional[str] = Form(None),
    pk_fin: Optional[str] = Form(None),
    pk_unique: Optional[str] = Form(None),
    observations: Optional[str] = Form(None),
    taches_json: str = Form("[]"),  # JSON array of taches
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    taches_data = json.loads(taches_json)
    report = DailyReport(
        user_id=user.id,
        type_travaux_id=type_travaux_id,
        type_travaux_autre=type_travaux_autre,
        pk_debut=pk_debut,
        pk_fin=pk_fin,
        pk_unique=pk_unique,
        observations=observations,
    )
    db.add(report)
    db.flush()

    for td in taches_data:
        tache = Tache(
            report_id=report.id,
            type_tache=td.get("type_tache"),
            type_implantation_id=td.get("type_implantation_id"),
            type_implantation_autre=td.get("type_implantation_autre"),
            type_reglage_id=td.get("type_reglage_id"),
            type_reglage_autre=td.get("type_reglage_autre"),
            description=td.get("description"),
        )
        db.add(tache)

    db.commit()
    db.refresh(report)
    return _format_report(report)

@router.post("/{report_id}/taches/{tache_id}/upload")
def upload_file(
    report_id: int,
    tache_id: int,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
    if not report or report.user_id != user.id and user.role != RoleEnum.super_admin.value:
        raise HTTPException(status_code=403, detail="Non autorisé")

    tache = db.query(Tache).filter(Tache.id == tache_id, Tache.report_id == report_id).first()
    if not tache:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")

    path = save_upload_file(file, subdir=f"reports/{report_id}")
    fichier = Fichier(
        tache_id=tache_id,
        nom_fichier=file.filename or "file",
        chemin_fichier=path,
        type_fichier=file.content_type,
    )
    db.add(fichier)
    db.commit()

    return {"message": "Fichier uploadé", "fichier_id": fichier.id}

@router.get("/", response_model=List[DailyReportResponse])
def list_reports(
    user_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(DailyReport)

    if user.role != RoleEnum.super_admin.value:
        # Membres/chefs voient leurs propres rapports
        if user.role == RoleEnum.chef_equipe.value:
            member_ids = [m.id for m in db.query(User).filter(User.chef_equipe_id == user.id).all()]
            query = query.filter(DailyReport.user_id.in_([user.id] + member_ids))
        else:
            query = query.filter(DailyReport.user_id == user.id)
    elif user_id:
        query = query.filter(DailyReport.user_id == user_id)

    reports = query.order_by(DailyReport.date.desc()).all()
    return [_format_report(r) for r in reports]

@router.get("/{report_id}", response_model=DailyReportResponse)
def get_report(report_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    return _format_report(report)

@router.delete("/{report_id}")
def delete_report(report_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    db.delete(report)
    db.commit()
    return {"message": "Rapport supprimé"}

# --- Summary for super admin ---
@router.get("/admin/summary")
def admin_summary(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    reports = db.query(DailyReport).order_by(DailyReport.date.desc()).all()
    total = len(reports)
    total_files = db.query(Fichier).count()
    receptions_pending = db.query(Reception).filter(Reception.mdc_signee == False).count()
    return {
        "total_reports": total,
        "total_files": total_files,
        "receptions_pending_mdc": receptions_pending,
        "reports": [_format_report(r) for r in reports],
    }

def _format_report(report: DailyReport):
    user = report.user
    taches = []
    for t in report.taches:
        fichiers = [
            FichierResponse(
                id=f.id, nom_fichier=f.nom_fichier,
                chemin_fichier=f.chemin_fichier,
                type_fichier=f.type_fichier, taille=f.taille,
                uploaded_at=f.uploaded_at,
            )
            for f in t.fichiers
        ]
        taches.append(TacheResponse(
            id=t.id, report_id=t.report_id,
            type_tache=t.type_tache,
            type_implantation_id=t.type_implantation_id,
            type_implantation_autre=t.type_implantation_autre,
            type_reglage_id=t.type_reglage_id,
            type_reglage_autre=t.type_reglage_autre,
            description=t.description,
            fichiers=fichiers,
        ))

    return DailyReportResponse(
        id=report.id, user_id=report.user_id,
        date=report.date,
        type_travaux_id=report.type_travaux_id,
        type_travaux_autre=report.type_travaux_autre,
        pk_debut=report.pk_debut, pk_fin=report.pk_fin,
        pk_unique=report.pk_unique, observations=report.observations,
        created_at=report.created_at, updated_at=report.updated_at,
        taches=taches,
        user_name=f"{user.nom} {user.prenoms}" if user else None,
    )
