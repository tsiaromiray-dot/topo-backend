from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class EquipementCreate(BaseModel):
    equipement: str

class UserCreate(BaseModel):
    nom: str
    prenoms: str
    matricule: str
    email: EmailStr
    password: str
    fonction: str
    role: Optional[str] = "membre"
    equipements: List[str] = []

class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenoms: Optional[str] = None
    fonction: Optional[str] = None
    equipements: Optional[List[str]] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    nom: str
    prenoms: str
    matricule: str
    email: str
    fonction: str
    role: str
    equipements: List[str] = []
    chef_equipe_id: Optional[int] = None
    is_active: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
