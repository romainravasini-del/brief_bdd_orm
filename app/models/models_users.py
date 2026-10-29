from enum import Enum
from sqlmodel import SQLModel, Field
from typing import Optional


# Définition des rôles autorisés
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin" #role pour v4


class User(SQLModel, table=True):
    __tablename__ = "users" # ou selon le nom de votre table utilisateur

    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    age: int
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)