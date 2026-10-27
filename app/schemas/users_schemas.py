import re
from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.users import NiveauAccesEnum


class UserCreateBase(BaseModel):
    nom: str = Field(min_length=1, max_length=50)
    prenom: str = Field(min_length=1, max_length=50)
    email: EmailStr
    is_active: bool = True


class ApprenantCreate(UserCreateBase):
    date_naissance: date
    niveau_etude: Optional[str] = Field(default=None, max_length=50)
    telephone: Optional[str] = None
    certification_obtenue: Optional[str] = Field(default=None, max_length=100)


    @field_validator("date_naissance")
    @classmethod
    def verifier_age(cls, v: date) -> date:
        aujourd_hui = date.today()
        age = aujourd_hui.year - v.year - ((aujourd_hui.month, aujourd_hui.day) < (v.month, v.day))

        if age < 16:
            raise ValueError("L'apprenant doit avoir au moins 16 ans !")
        return v

    @field_validator("telephone")
    @classmethod
    def verifier_telephone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not re.match(r"^0[1-9]\d{8}$", v):
            raise ValueError("Le téléphone doit contenir 10 chiffres (ex: 0612345678).")
        return v



class FormateurCreate(UserCreateBase):
    specialite: str = Field(min_length=1, max_length=100)
    date_embauche: date
    taux_horaire: float = Field(ge=0)
    bio: Optional[str] = None


    @field_validator("date_embauche")
    @classmethod
    def verifier_date_embauche(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("La date d'embauche doit être antérieure à aujourd'hui !")
        return v


class StaffCreate(UserCreateBase):
    poste: str = Field(min_length=1, max_length=100)
    date_prise_fonction: date
    responsabilites: Optional[dict] = None


class AdminCreate(UserCreateBase):
    niveau_acces: NiveauAccesEnum = NiveauAccesEnum.ADMIN_STANDARD
    date_promotion: date