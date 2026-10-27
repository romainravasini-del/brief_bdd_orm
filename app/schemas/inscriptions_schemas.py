from datetime import datetime
from typing import Optional
from pydantic import Field, BaseModel
from app.models.inscriptions import StatutInscriptionEnum

class InscriptionCreate(BaseModel):
    apprenant_id: int = Field(ge=1)
    session_id: int = Field(ge=1)
    statut_inscription: StatutInscriptionEnum = Field(default=StatutInscriptionEnum.ENREGISTRE)
    presence : Optional[bool] = Field (default=None)

class InscriptionUpdate(BaseModel):
    statut_inscription: Optional[StatutInscriptionEnum] = None
    presence: Optional[bool] = None

class InscriptionRead(InscriptionCreate):
    id: int                 
    date_inscription: datetime
    