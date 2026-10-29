import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

# 1. Charger l'URL depuis le fichier .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cftech.db")

# 2. Créer le moteur SQLModel
engine = create_engine(DATABASE_URL, echo=True)


# 3. Fonction pour créer toutes les tables définies avec SQLModel
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# 4. Fonction pour obtenir une session SQLModel
def get_session():
    with Session(engine) as session:
        yield session
