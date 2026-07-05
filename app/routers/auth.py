from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserEquipement, RoleEnum
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth import hash_password, verify_password, create_access_token, decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token invalide")
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé ou désactivé")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != RoleEnum.super_admin.value:
        raise HTTPException(status_code=403, detail="Accès réservé au super admin")
    return user

@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.email == data.email) | (User.matricule == data.matricule)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ou matricule déjà utilisé")

    user = User(
        nom=data.nom,
        prenoms=data.prenoms,
        matricule=data.matricule,
        email=data.email,
        password_hash=hash_password(data.password),
        fonction=data.fonction,
        role=data.role or RoleEnum.membre.value,
    )
    db.add(user)
    db.flush()

    for equip in data.equipements:
        db.add(UserEquipement(user_id=user.id, equipement=equip))
    db.commit()
    db.refresh(user)

    return {"message": "Compte créé avec succès", "user_id": user.id}

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Compte désactivé")

    token = create_access_token({"sub": str(user.id)})
    equipements = [e.equipement for e in user.equipements]
    user_resp = UserResponse(
        id=user.id, nom=user.nom, prenoms=user.prenoms,
        matricule=user.matricule, email=user.email,
        fonction=user.fonction, role=user.role,
        equipements=equipements, chef_equipe_id=user.chef_equipe_id,
        is_active=user.is_active,
    )
    return Token(access_token=token, token_type="bearer", user=user_resp)
