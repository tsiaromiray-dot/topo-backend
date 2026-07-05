from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class TypeTravaux(Base):
    __tablename__ = "type_travaux"
    id = Column(Integer, primary_key=True, index=True)
    categorie = Column(String(50), nullable=False)  # Chaussée, Assainissement, OH, OA
    nom = Column(String(100), nullable=False)
    is_active = Column(Integer, default=1)

class TypeImplantation(Base):
    __tablename__ = "type_implantations"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False, unique=True)
    is_active = Column(Integer, default=1)

class TypeReglage(Base):
    __tablename__ = "type_reglages"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False, unique=True)
    is_active = Column(Integer, default=1)
