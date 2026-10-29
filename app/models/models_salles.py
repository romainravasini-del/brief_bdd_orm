from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, JSON


class Salle(SQLModel, table=True):
    """
    Modèle de salle (Migration v3 avec support JSON pour les équipements)
    """
    __tablename__ = "salle"

    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(unique=True, nullable=False)
    capacite: int = Field(nullable=False)
    localisation: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    
    #  Nouveau champ de la v3 : Stockage des équipements sous forme de liste JSON
    equipements: Optional[list] = Field(default=None, sa_column=Column(JSON))