from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User, RoleEnum
from app.models.report import DailyReport, Tache, Fichier
from app.models.reception import Reception
from app.schemas.report import DailyReportResponse, TacheResponse, FichierResponse
from app.schemas.reception import ReceptionResponse
from app.routers.auth import get_current_user
from sqlalchemy import or_

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/", response_model=dict)
def search_all(
    q: str = Query(..., min_length=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search across reports and receptions by PK, type, description, etc."""
    # Search reports
    report_query = db.query(DailyReport)
    if user.role != RoleEnum.super_admin.value:
        if user.role == RoleEnum.chef_equipe.value:
            member_ids = [m.id for m in db.query(User).filter(User.chef_equipe_id == user.id).all()]
            report_query = report_query.filter(DailyReport.user_id.in_([user.id] + member_ids))
        else:
            report_query = report_query.filter(DailyReport.user_id == user.id)

    reports = report_query.filter(
        or_(
            DailyReport.pk_debut.ilike(f"%{q}%"),
            DailyReport.pk_fin.ilike(f"%{q}%"),
            DailyReport.pk_unique.ilike(f"%{q}%"),
            DailyReport.observations.ilike(f"%{q}%"),
        )
    ).all()

    # Search receptions
    rec_query = db.query(Reception)
    if user.role != RoleEnum.super_admin.value:
        if user.role == RoleEnum.chef_equipe.value:
            member_ids = [m.id for m in db.query(User).filter(User.chef_equipe_id == user.id).all()]
            sub = db.query(DailyReport.id).filter(
                DailyReport.user_id.in_([user.id] + member_ids)
            ).subquery()
            rec_query = rec_query.filter(Reception.report_id.in_(sub))
        else:
            sub = db.query(DailyReport.id).filter(DailyReport.user_id == user.id).subquery()
            rec_query = rec_query.filter(Reception.report_id.in_(sub))

    receptions = rec_query.filter(
        or_(
            Reception.type_travaux.ilike(f"%{q}%"),
            Reception.pk.ilike(f"%{q}%"),
            Reception.description.ilike(f"%{q}%"),
        )
    ).all()

    return {
        "query": q,
        "reports_count": len(reports),
        "receptions_count": len(receptions),
        "reports": [_format_report(r) for r in reports],
        "receptions": receptions,
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
