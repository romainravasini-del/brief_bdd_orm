from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from app.models.sessions import StatutSessionEnum


# 1. Schéma Pydantic pour créer une Salle
class SalleCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=50)
    capacite: int = Field(ge=1)  # Doit être >= 1
    localisation: str = Field(min_length=1, max_length=150)
    equipements: Optional[dict] = None  # Dictionnaire JSON
    is_active: bool = True


# 2. Schéma Pydantic pour créer une Session de formation
class SessionCreate(BaseModel):
    titre: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    date_debut: datetime
    date_fin: datetime
    salle_id: int = Field(ge=1)
    formateur_id: int = Field(ge=1)
    capacite_max: int = Field(ge=1)
    statut: StatutSessionEnum = StatutSessionEnum.OPEN
    prerequis: Optional[dict] = None

    # Vérifie que la date de fin est bien APRÈS la date de début !
    @model_validator(mode="after")
    def verifier_dates(self):
        if self.date_fin <= self.date_debut:
            raise ValueError("La date de fin doit être après la date de début !")
        return self