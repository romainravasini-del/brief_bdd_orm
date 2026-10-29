import sys
import time
from sqlmodel import Session, create_engine, select, delete
from app.models.models_users import User, UserRole
from app.models.models_salles import Salle
from app.models.models_sessions import TrainingSession


# Connexion ciblée 
sqlite_url = "sqlite:///cftech.db"
engine = create_engine(sqlite_url, echo=False)

def reset_database():
    """Remet à zéro toutes les données de la base avec la syntaxe SQLModel moderne."""
    print(" Nettoyage de la base de données...")
    with Session(engine) as session:
        # Utilisation de delete() compatible SQLModel 2.0+ pour éviter les warnings
        session.exec(delete(TrainingSession))
        session.exec(delete(User))
        session.exec(delete(Salle))
        session.commit()
    print("✅ Base de données nettoyée avec succès !\n")


def run_demo():
    
    # Nettoyage automatique au lancement pour éviter les doublons
    reset_database()
    time.sleep(1)
    
    print(" Lancement de la démonstration des fonctionnalités CF-Tech (Mode Tech)...\n")
    time.sleep(1.2)
    
    with Session(engine) as session:
        # 1. Test des rôles Utilisateurs (User, Admin, SuperAdmin)
        print(" 1. Création des profils utilisateurs (Développeur, DevOps, Lead Architect)...")
        time.sleep(1)
        user1 = User(nom="Alice Dev", email="alice@cftech.test", age=28, role=UserRole.USER, is_active=True)
        user2 = User(nom="Bob DevOps", email="bob@cftech.test", age=35, role=UserRole.ADMIN, is_active=True)
        user3 = User(nom="Xavier Architecte", email="xavier@cftech.test", age=48, role=UserRole.SUPERADMIN, is_active=True)
        
        session.add_all([user1, user2, user3])
        session.commit()
        print("    Utilisateurs créés avec leurs rôles respectifs.\n")
        time.sleep(1.5)

        # 2. Test de la table Salles / Labs avec le champ JSON 'equipements'
        print(" 2. Création d'un Lab informatique avec équipements techniques (JSON)...")
        time.sleep(1)
        salle1 = Salle(
            nom="CF-Tech Server Lab - Alpha",
            localisation="42 Rue du Code, 75001 Paris",
            capacite=25,
            is_active=True,
            equipements=[
                "Serveurs Rackables Dell PowerEdge",
                "Switches Cisco Catalyst 48 ports",
                "Postes de travail Linux Ubuntu / VS Code",
                "NAS Synology 16To",
                "Onduleurs UPS redondants"
            ]
        )
        session.add(salle1)
        session.commit()
        session.refresh(salle1)
        print(f"    Lab '{salle1.nom}' (Capacité : {salle1.capacite} postes) enregistré avec la stack :\n      -> {salle1.equipements}\n")
        time.sleep(1.5)

        # 3. Test des Sessions de travail / technique
        print(" 3. Création d'une session de travail technique...")
        time.sleep(1)
        session_train = TrainingSession(
            user_id=user1.id,
            salle_id=salle1.id,
            titre="Atelier Migration SQLModel & Alembic",
            duree_minutes=120
        )
        session.add(session_train)
        session.commit()
        print("    Session technique liée au développeur et au Lab.\n")
        time.sleep(1.5)

        # 4. Affichage global pour la démonstration (lecture en base)
        print(" --- RAPPORT DE LA BASE DE DONNÉES (DEMO TECH) ---")
        time.sleep(1)
        
        # Affichage des utilisateurs
        users = session.exec(select(User)).all()
        print(f"\n[Utilisateurs enregistrés : {len(users)}]")
        for u in users:
            print(f"   - {u.nom} ({u.email}) | Rôle :  {u.role.value.upper()}")
            time.sleep(0.4)

        # Affichage des salles / labs
        salles = session.exec(select(Salle)).all()
        print(f"\n[Labs / Salles enregistrés : {len(salles)}]")
        for s in salles:
            print(f"   - {s.nom} | Localisation : {s.localisation} | Capacité : {s.capacite}")
            print(f"     Matériel / Stack : {s.equipements}")
            time.sleep(0.4)

        print("\n Démonstration exécutée avec succès !")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_database()
    else:
        run_demo()