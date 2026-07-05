from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base, SessionLocal
from app.config import settings
from app.routers import auth, users, choices, reports, receptions, search
import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Seed default choices
def seed_choices():
    db = SessionLocal()
    try:
        from app.models.choices import TypeTravaux, TypeImplantation, TypeReglage
        from app.models.user import User, RoleEnum
        from app.services.auth import hash_password

        # Seed admin user if not exists
        admin_email = "tsiaromiray@gmail.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin = User(
                nom="Admin",
                prenoms="Topo",
                matricule="ADMIN001",
                email=admin_email,
                password_hash=hash_password("fandresena"),
                fonction="Responsable Topo",
                role=RoleEnum.super_admin.value,
            )
            db.add(admin)
            db.commit()

        categories = {
            "Chaussée": ["Entrée en terre", "PST", "CF", "CB", "BBSG", "Autres"],
            "Assainissement": ["Assainissement"],
            "Ouvrage Hydraulique": ["Ouvrage Hydraulique"],
            "Ouvrage d'Art": ["Ouvrage d'Art"],
        }
        for cat, noms in categories.items():
            for nom in noms:
                existing = db.query(TypeTravaux).filter(
                    TypeTravaux.categorie == cat, TypeTravaux.nom == nom
                ).first()
                if not existing:
                    db.add(TypeTravaux(categorie=cat, nom=nom))

        # Seed implantations defaults
        for nom in ["PST", "CF", "CB", "BBSG", "Autres"]:
            existing = db.query(TypeImplantation).filter(TypeImplantation.nom == nom).first()
            if not existing:
                db.add(TypeImplantation(nom=nom))

        # Seed reglages defaults
        for nom in ["PST", "CF", "CB", "BBSG", "Autres"]:
            existing = db.query(TypeReglage).filter(TypeReglage.nom == nom).first()
            if not existing:
                db.add(TypeReglage(nom=nom))

        db.commit()
    finally:
        db.close()

app = FastAPI(title="Topo App API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(choices.router)
app.include_router(reports.router)
app.include_router(receptions.router)
app.include_router(search.router)

# Static files (uploads)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

@app.on_event("startup")
def startup():
    seed_choices()

@app.get("/")
def root():
    return {"message": "Topo App API - Bienvenue"}

@app.get("/health")
def health():
    return {"status": "ok"}
