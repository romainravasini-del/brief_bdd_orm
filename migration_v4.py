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

def run_demo_v4():
    print("============================================================")
    print("🚀 DÉMONSTRATION FINALE & VALIDATION DE LA MIGRATION V4 (SUPERADMIN)")
    print("============================================================\n")
    
    reset_database()
    time.sleep(0.5)

    with Session(engine) as session:
        # 1. Test des différents rôles (User, Admin, SuperAdmin)
        print("1️⃣  Création des profils avec les différents niveaux de rôles (v4)...")
        alice = User(nom="Alice Dev", email="alice@cftech.test", age=28, role=UserRole.USER, is_active=True)
        bob = User(nom="Bob DevOps", email="bob@cftech.test", age=35, role=UserRole.ADMIN, is_active=True)
        xavier = User(nom="Xavier Architecte", email="xavier@cftech.test", age=48, role=UserRole.SUPERADMIN, is_active=True)
        
        session.add_all([alice, bob, xavier])
        session.commit()
        print("   -> Utilisateurs créés avec succès.\n")

        # 2. Création d'une salle avec équipements (v3)
        print("2️⃣  Création du Lab technique (v3)...")
        salle_lab = Salle(
            nom="CF-Tech Server Lab - Alpha",
            localisation="42 Rue du Code, 75001 Paris",
            capacite=25,
            is_active=True,
            equipements=["Serveurs Dell PowerEdge", "Switches Cisco", "NAS Synology"]
        )
        session.add(salle_lab)
        session.commit()
        session.refresh(salle_lab)
        print("   -> Lab enregistré.\n")

        # 3. Création d'une session avec statut (v2)
        print("3️⃣  Création d'une session de formation (v2)...")
        session_train = TrainingSession(
            user_id=alice.id,
            salle_id=salle_lab.id,
            titre="Atelier Migration & Architecture",
            description="Maîtrise complète d'Alembic et SQLModel",
            statut=StatutSessionEnum.OPEN
        )
        session.add(session_train)
        session.commit()
        print("   -> Session enregistrée.\n")
        time.sleep(0.5)

        # 4. Rapport global final
        print("============================================================")
        print("📊 RAPPORT FINAL DE LA BASE DE DONNÉES (V1 + V2 + V3 + V4)")
        print("============================================================")
        
        users_db = session.exec(select(User)).all()
        print(f"\n[Utilisateurs enregistrés : {len(users_db)}]")
        for u in users_db:
            role_badge = {
                UserRole.USER: "👤 [USER]",
                UserRole.ADMIN: "🛡️ [ADMIN]",
                UserRole.SUPERADMIN: "⭐ [SUPERADMIN - V4 VALIDÉ]"
            }.get(u.role, f"❓ [{u.role}]")
            print(f"   • {u.nom} ({u.email}) | Rôle : {role_badge}")

        salles_db = session.exec(select(Salle)).all()
        print(f"\n[Salles / Labs enregistrés : {len(salles_db)}]")
        for s in salles_db:
            print(f"   • {s.nom} | Équipements JSON (v3) : {s.equipements}")

        sessions_db = session.exec(select(TrainingSession)).all()
        print(f"\n[Sessions enregistrées : {len(sessions_db)}]")
        for ses in sessions_db:
            print(f"   • {ses.titre} | Statut (v2) : {ses.statut}")

        print("\n============================================================")
        print("🎉 TOUTES LES MIGRATIONS (V1 à V4) SONT VALIDÉES AVEC SUCCÈS !")
        print("============================================================\n")

if __name__ == "__main__":
    run_demo_v4()