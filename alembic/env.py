import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context


# Ajoute la racine du projet au PYTHONPATH pour qu'Alembic trouve le dossier 'app'
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Importe SQLModel et ses modèles 
from sqlmodel import SQLModel
from app.models.models_users import User  
from app.models.models_sessions import TrainingSession  # <-- Importation du nouveau modèle
from app.models.models_salles import Salle

from sqlmodel import SQLModel
# Modèles historiques des premières migrations Alembic (Xavier)
from app.models.models_users import User  
from app.models.models_sessions import TrainingSession
# Modèles complets de l'application CF-Tech (Romain)
from app.models.salles import Salle
from app.models.users import Apprenant, Formateur, StaffPedagogique, Admin
from app.models.sessions import SessionFormation
from app.models.inscriptions import Inscription


# Objet de configuration Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. Liaison importante pour SQLModel
target_metadata = SQLModel.metadata

# --- Code généré par défaut par Alembic ---

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()