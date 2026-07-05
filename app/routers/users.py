from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User, UserEquipement, RoleEnum
from app.schemas.user import UserResponse, UserUpdate
from app.routers.auth import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    equipements = [e.equipement for e in user.equipements]
    return UserResponse(
        id=user.id, nom=user.nom, prenoms=user.prenoms,
        matricule=user.matricule, email=user.email,
        fonction=user.fonction, role=user.role,
        equipements=equipements, chef_equipe_id=user.chef_equipe_id,
        is_active=user.is_active,
    )

@router.put("/me")
def update_me(data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.nom is not None:
        user.nom = data.nom
    if data.prenoms is not None:
        user.prenoms = data.prenoms
    if data.fonction is not None:
        user.fonction = data.fonction
    if data.equipements is not None:
        db.query(UserEquipement).filter(UserEquipement.user_id == user.id).delete()
        for equip in data.equipements:
            db.add(UserEquipement(user_id=user.id, equipement=equip))
    db.commit()
    return {"message": "Profil mis à jour"}

@router.get("/", response_model=List[UserResponse])
def list_users(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []
    for u in users:
        equipements = [e.equipement for e in u.equipements]
        result.append(UserResponse(
            id=u.id, nom=u.nom, prenoms=u.prenoms,
            matricule=u.matricule, email=u.email,
            fonction=u.fonction, role=u.role,
            equipements=equipements, chef_equipe_id=u.chef_equipe_id,
            is_active=u.is_active,
        ))
    return result

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    equipements = [e.equipement for e in u.equipements]
    return UserResponse(
        id=u.id, nom=u.nom, prenoms=u.prenoms,
        matricule=u.matricule, email=u.email,
        fonction=u.fonction, role=u.role,
        equipements=equipements, chef_equipe_id=u.chef_equipe_id,
        is_active=u.is_active,
    )

@router.delete("/{user_id}")
def delete_user(user_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    u.is_active = 0
    db.commit()
    return {"message": "Utilisateur désactivé"}
