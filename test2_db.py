import os
import sqlite3
import time
from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlalchemy.exc import IntegrityError

# 1. Chemin absolu vers votre base cftech-2.db
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, "cftech-2.db")

print(f"🔍 [DIAGNOSTIC] Vérification du fichier : {db_path}")
print(f"📁 Le fichier existe sur le disque ? {os.path.exists(db_path)}")
if os.path.exists(db_path):
    print(f"📊 Taille du fichier : {os.path.getsize(db_path)} octets")

    # Diagnostic brut avec sqlite3 pour voir ce que la base contient VRAIMENT
    conn_brute = sqlite3.connect(db_path)
    cursor = conn_brute.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables_trouvees = cursor.fetchall()
    conn_brute.close()
    print(f"📋 Tables présentes dans ce fichier : {tables_trouvees}")
else:
    print("❌ ATTENTION : Le fichier n'existe pas à cet endroit précis !")

print("-" * 50)

# 2. Connexion SQLAlchemy
sqlite_url = f"sqlite:///{db_path.replace(os.sep, '/')}"
engine = create_engine(sqlite_url, echo=False)

# --- Définition des modèles ---

class Salle(SQLModel, table=True):
    __tablename__ = "salle"
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(unique=True, nullable=False)
    capacite: int = Field(nullable=False)
    localisation: str = Field(nullable=False)
    equipements: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)

class Apprenant(SQLModel, table=True):
    __tablename__ = "apprenant"
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(nullable=False)
    prenom: str = Field(nullable=False)
    email: str = Field(unique=True, nullable=False)
    date_creation: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    role: str = Field(default="apprenant")
    date_naissance: date = Field(nullable=False)
    niveau_etude: Optional[str] = Field(default=None)
    telephone: Optional[str] = Field(default=None)
    date_inscription_plateforme: datetime = Field(default_factory=datetime.utcnow)
    certification_obtenue: Optional[str] = Field(default=None)


def run_demo():
    print("🚀 Lancement de l'injection de données...\n")
    time.sleep(0.3)
    
    with Session(engine) as session:
        salle_nom = "Labo AI & Cloud"
        existing_salle = session.exec(select(Salle).where(Salle.nom == salle_nom)).first()
        if not existing_salle:
            nouvelle_salle = Salle(
                nom=salle_nom,
                capacite=15,
                localisation="Bâtiment Sud, 1er étage",
                equipements='["GPU H100", "Ecrans 4K"]',
                is_active=True
            )
            session.add(nouvelle_salle)
            print(f"➕ [Salle] Ajoutée : {salle_nom}")
        else:
            print(f"ℹ️ [Salle] La salle '{salle_nom}' existe déjà, ignorée.")

        try:
            session.commit()
            print("\n✅ Modification enregistrée avec succès !")
        except IntegrityError as e:
            session.rollback()
            print(f"\n⚠️ Erreur d'intégrité SQL : {e}")

if __name__ == "__main__":
    run_demo()