from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum

#class StatutSessionEnum a liberer pour la V2 alembic
class StatutSessionEnum(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class TrainingSession(SQLModel, table=True):
    """
    Modèle représentant une session (de cours ou d'entraînement) dans le projet CF-Tech.
    Utilise SQLModel pour lier la classe Python directement à la table SQL 'training_sessions'.
    """
    __tablename__ = "training_sessions"

    # Identifiant unique de la session (clé primaire auto-incrémentée)
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    # Titre ou libellé de la session
    titre: str = Field(index=True, description="Titre descriptif de la session")

    # Champ clé demandé : statut de la session ('ouverte' par défaut, ou 'fermee')
    statut_session: str = Field(
        default="ouverte", 
        description="Indique si la session est 'ouverte' ou 'fermee'"
    )

    # Description optionnelle de la session
    description: Optional[str] = Field(default=None, description="Détails optionnels sur la session")
    # a liberer pour la V2
    statut: StatutSessionEnum = Field(default=StatutSessionEnum.OPEN)
