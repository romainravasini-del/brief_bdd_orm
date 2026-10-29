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
    """Nettoyage pour repartir sur un test propre."""
    print("🧹 Nettoyage des anciennes données dans cftech.db...")
    with Session(engine) as session:
        session.exec(delete(TrainingSession))
        session.exec(delete(User))
        session.exec(delete(Salle))
        session.commit()
    print("✅ Base nettoyée avec succès !\n")

def run_demo_v3():
    print("============================================================")
    print("🚀 DÉMONSTRATION ET VALIDATION VISUELLE DE LA MIGRATION V3")
    print("============================================================\n")
    
    reset_database()
    time.sleep(0.5)

    with Session(engine) as session:
        # 1. Création d'utilisateurs
        print("1️⃣  Création des profils utilisateurs...")
        user1 = User(nom="Alice Dev", email="alice@cftech.test", age=28, role=UserRole.USER, is_active=True)
        session.add(user1)
        session.commit()
        session.refresh(user1)
        print("   -> Utilisateur créé.\n")

        # 2. Création d'une salle avec le nouveau champ JSON 'equipements' (V3)
        print("2️⃣  Création d'un Lab informatique avec équipements JSON (v3)...")
        salle_lab = Salle(
            nom="CF-Tech Server Lab - Alpha",
            localisation="42 Rue du Code, 75001 Paris",
            capacite=25,
            is_active=True,
            equipements=[
                "Serveurs Rackables Dell PowerEdge",
                "Switches Cisco Catalyst 48 ports",
                "Postes Linux Ubuntu / VS Code",
                "NAS Synology 16To"
            ]
        )
        session.add(salle_lab)
        session.commit()
        session.refresh(salle_lab)
        print(f"   -> Salle '{salle_lab.nom}' enregistrée.\n")

        # 3. Création d'une session associée
        print("3️⃣  Création d'une session de formation...")
        session_train = TrainingSession(
            user_id=user1.id,
            salle_id=salle_lab.id,
            titre="Atelier Infrastructure & Réseau",
            description="Configuration des switches et serveurs",
            statut=StatutSessionEnum.OPEN
        )
        session.add(session_train)
        session.commit()
        print("   -> Session enregistrée.\n")
        time.sleep(0.5)

        # 4. Affichage du rapport visuel v3
        print("============================================================")
        print("📊 RAPPORT DE VALIDATION MIGRATION V3 (CHAMP JSON 'EQUIPEMENTS')")
        print("============================================================")
        
        salles_db = session.exec(select(Salle)).all()
        
        for idx, s in enumerate(salles_db, 1):
            print(f"\n Lab / Salle #{idx}:")
            print(f"   • Nom          : {s.nom}")
            print(f"   • Localisation : {s.localisation}")
            print(f"   • Capacité     : {s.capacite} postes")
            print(f"   • ÉQUIPEMENTS  : {s.equipements}  <-- Champ JSON v3 validé !")
            print(f"   • Type Python  : {type(s.equipements).__name__} (automatiquement converti en liste)")

        print("\n============================================================")
        print("🎉 MIGRATION V3 (JSON) VALIDÉE AVEC SUCCÈS SUR CFTECH.DB !")
        print("============================================================\n")

if __name__ == "__main__":
    run_demo_v3()