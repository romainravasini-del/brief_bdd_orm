from enum import Enum
from sqlmodel import SQLModel, Field

# Définition des rôles autorisés
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    nom: str
    email: str
    age: int | None = None
    # On utilise l'Enum avec une valeur par défaut à 'user'
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)