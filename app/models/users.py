from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import EmailStr


class NiveauAccesEnum(str, Enum):
    ADMIN_STANDARD = "ADMIN_STANDARD"
    ADMIN_RESEAU = "ADMIN_RESEAU"
    # Ajouté par migration Alembic v4 :
    # SUPERADMIN = "SUPERADMIN"

# 1. Classe mère abstraite (table=False) : partage les champs communs
class UserBase(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(max_length=50)
    prenom: str = Field(max_length=50)
    email: EmailStr= Field(unique=True, index=True, max_length = 255)
    date_creation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)
    
    @property 
    def role(self) -> str:
        return {
            "Apprenant": "apprenant",
            "Formateur": "formateur",
            "StaffPedagogique": "staff",
            "Admin": "admin",
        }.get(self.__class__.__name__, "inconnu")

# 2. Les 4 tables SQL créées par héritage (table=True)
class Apprenant(UserBase, table=True):
    __tablename__ = "apprenants"    
    date_naissance: date
    niveau_etude: Optional[str] = Field(default=None, max_length=50)
    telephone: Optional[str] = Field(default=None, max_length=20)
    date_inscription_plateforme: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    certification_obtenue: Optional[str] = Field(default=None, max_length=100)

class Formateur(UserBase, table=True):
    __tablename__ = "formateurs"
    specialite: str = Field(max_length=100)
    date_embauche: date
    taux_horaire: float = Field(ge=0)
    bio: Optional[str] = Field(default=None)
   
class StaffPedagogique(UserBase, table=True):
    __tablename__ = "staff_pedagogiques"
    poste: str = Field(max_length=100)
    date_prise_fonction: date
    responsabilites: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    @property
    def role(self) -> str:
        return "staff"

class Admin(UserBase, table=True):
    __tablename__ = "admins"
    niveau_acces: NiveauAccesEnum = Field(default=NiveauAccesEnum.ADMIN_STANDARD)
    date_promotion: date

    @property
    def role(self) -> str:
        return self.niveau_acces.lower()