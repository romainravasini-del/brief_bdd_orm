from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON

class StatutSessionEnum(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class SessionFormation(SQLModel, table=True):
    __tablename__ = "sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    titre: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    date_debut: datetime
    date_fin: datetime
    salle_id: int = Field(foreign_key="salles.id")
    formateur_id: int = Field(foreign_key="formateurs.id")
    capacite_max: int = Field(ge=1)
    statut: StatutSessionEnum = Field(default=StatutSessionEnum.OPEN)
    prerequis: Optional[dict] = Field(default=None, sa_column=Column(JSON))