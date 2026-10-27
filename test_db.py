from sqlmodel import Session, select
from app.database import engine
from app.models.models_users import User

def test_database():
    # 1. Insertion d'un utilisateur de test
    with Session(engine) as session:
        # Vérif si l'email existe
        existing_user = session.exec(select(User).where(User.email == "xavier@cftech.test")).first()
        
        if not existing_user:
            new_user = User(
                nom="Xavier",
                email="xavier@cftech.test",
                age=48,
                role="admin",
                is_active=True
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            print(f" Utilisateur inséré avec succès : ID {new_user.id} - {new_user.nom}")
        else:
            print(f" L'utilisateur existe déjà dans la base (ID {existing_user.id}).")

    # 2. Lecture et affichage de tous les utilisateurs de la table
    with Session(engine) as session:
        statement = select(User)
        users = session.exec(statement).all()
        
        print("\n Liste des utilisateurs enregistrés dans 'cftech.db' :")
        for u in users:
            print(f"   - [ID: {u.id}] {u.nom} ({u.email}) - Rôle : {u.role} - Actif : {u.is_active}")

if __name__ == "__main__":
    test_database()