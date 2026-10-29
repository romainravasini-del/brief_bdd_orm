from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON


class Salle(SQLModel, table=True):
    __tablename__ = "salles"

    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(unique=True, index=True, max_length=50)
    capacite: int = Field(ge=1)  # Doit être >= 1
    localisation: str = Field(max_length=150)
    equipements: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    is_active: bool = Field(default=True)