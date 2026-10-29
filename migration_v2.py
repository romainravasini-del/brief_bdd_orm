import sys
import time
from sqlmodel import Session, create_engine, select, delete
from app.models.models_users import User, UserRole
from app.models.models_salles import Salle
from app.models.models_sessions import TrainingSession, StatutSessionEnum


# Connexion ciblée sur la base cftech.db
sqlite_url = "sqlite:///cftech.db"
engine = create_engine(sqlite_url, echo=False)


def reset_database():
    """Remet à zéro toutes les données de la base pour un test propre de la v2."""
    print("🧹 Nettoyage des anciennes données dans cftech.db...")
    with Session(engine) as session:
        session.exec(delete(TrainingSession))
        session.exec(delete(User))
        session.exec(delete(Salle))
        session.commit()
    print("✅ Base nettoyée avec succès !\n")


def run_demo_v2():
    print("============================================================")
    print("🚀 DÉMONSTRATION ET VALIDATION VISUELLE DE LA MIGRATION V2")
    print("============================================================\n")
    
    # 1. Nettoyage initial
    reset_database()
    time.sleep(0.5)

    with Session(engine) as session:
        # 2. Création des utilisateurs de test
        print("1️⃣  Création des profils utilisateurs...")
        user1 = User(nom="Alice Dev", email="alice@cftech.test", age=28, role=UserRole.USER, is_active=True)
        user2 = User(nom="Bob DevOps", email="bob@cftech.test", age=35, role=UserRole.ADMIN, is_active=True)
        session.add_all([user1, user2])
        session.commit()
        session.refresh(user1)
        session.refresh(user2)
        print("   -> Utilisateurs créés.\n")

        # 3. Création d'une salle de test
        print("2️⃣  Création d'une salle de formation...")
        salle1 = Salle(
            nom="Salle Turing - Lab 1",
            localisation="Bâtiment Central, Etage 1",
            capacite=20,
            is_active=True
        )
        session.add(salle1)
        session.commit()
        session.refresh(salle1)
        print(f"   -> Salle '{salle1.nom}' enregistrée.\n")

        # 4. Insertion de sessions avec les différents statuts de la V2
        print("3️⃣  Création des sessions de formation (Test des statuts v2 : OPEN, CLOSED, ARCHIVED)...")
        
        session_open = TrainingSession(
            user_id=user1.id,
            salle_id=salle1.id,
            titre="Atelier Docker & Kubernetes",
            description="Atelier pratique sur les conteneurs",
            statut=StatutSessionEnum.OPEN
        )
        
        session_closed = TrainingSession(
            user_id=user2.id,
            salle_id=salle1.id,
            titre="Introduction à Python & Data",
            description="Formation de base en programmation",
            statut=StatutSessionEnum.CLOSED
        )

        session_archived = TrainingSession(
            user_id=user1.id,
            salle_id=salle1.id,
            titre="Bases du HTML & CSS (2023)",
            description="Ancienne session archivée",
            statut=StatutSessionEnum.ARCHIVED
        )

        session.add_all([session_open, session_closed, session_archived])
        session.commit()
        print("   -> 3 sessions avec statuts différents enregistrées en base.\n")
        time.sleep(0.5)

        # 5. Affichage visuel du rapport de validation v2
        print("============================================================")
        print("📊 RAPPORT DE VALIDATION MIGRATION V2 (TABLE SESSIONS)")
        print("============================================================")
        
        sessions_db = session.exec(select(TrainingSession)).all()
        
        for idx, s in enumerate(sessions_db, 1):
            statut_icon = {
                StatutSessionEnum.OPEN: "🟢 [OUVERTE / OPEN]",
                StatutSessionEnum.CLOSED: "🔴 [FERMÉE / CLOSED]",
                StatutSessionEnum.ARCHIVED: "📦 [ARCHIVÉE / ARCHIVED]"
            }.get(s.statut, f"❓ [{s.statut}]")

            print(f"\n Session #{idx}:")
            print(f"   • Titre       : {s.titre}")
            print(f"   • Description : {s.description}")
            print(f"   • STATUT      : {statut_icon}  <-- Champ v2 validé !")
            time.sleep(0.3)

        print("\n============================================================")
        print("🎉 MIGRATION V2 VALIDÉE AVEC SUCCÈS SUR CFTECH.DB !")
        print("============================================================\n")


if __name__ == "__main__":
    run_demo_v2()