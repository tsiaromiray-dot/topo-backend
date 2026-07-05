from sqlalchemy import Column, Integer, String, Enum as SAEnum, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class FonctionEnum(str, enum.Enum):
    topographe_operateur = "Topographe/Opérateur"
    chef_brigade = "Chef de brigade"
    responsable_topo = "Responsable Topo"
    cadre_topo = "Cadre Topo"

class EquipementEnum(str, enum.Enum):
    station_totale = "Station totale"
    niveau = "Niveau"
    gps = "GPS"
    drone = "Drone"
    autres = "Autres"

class RoleEnum(str, enum.Enum):
    super_admin = "super_admin"
    chef_equipe = "chef_equipe"
    membre = "membre"

# Association table: user <-> equipements
user_equipements = Table(
    "user_equipements",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("equipement", String(50)),  # stores enum value
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenoms = Column(String(100), nullable=False)
    matricule = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    fonction = Column(String(50), nullable=False)  # FonctionEnum value
    role = Column(String(20), default=RoleEnum.membre.value)  # RoleEnum value
    chef_equipe_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Integer, default=1)

    # Relationships
    chef_equipe = relationship("User", remote_side=[id], backref="membres")
    equipements = relationship("UserEquipement", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("DailyReport", back_populates="user", cascade="all, delete-orphan")

class UserEquipement(Base):
    __tablename__ = "user_equipements_table"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    equipement = Column(String(50), nullable=False)

    user = relationship("User", back_populates="equipements")
