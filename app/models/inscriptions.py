from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint
class StatutInscriptionEnum(str, Enum):
    ENREGISTRE = "ENREGISTRE"
    DESINSCRIT = "DESINSCRIT"
    EN_ATTENTE = "EN_ATTENTE"


class Inscription(SQLModel, table=True):
    __tablename__ = "inscriptions"
    __table_args__ = (
        UniqueConstraint("apprenant_id", "session_id", name="uq_apprenant_session"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    apprenant_id: int = Field(foreign_key="apprenants.id")
    session_id: int = Field(foreign_key="sessions.id")
    date_inscription: datetime = Field(default_factory=datetime.now)
    statut_inscription: StatutInscriptionEnum = Field(default=StatutInscriptionEnum.ENREGISTRE)
    presence: Optional[bool] = Field(default=None)
