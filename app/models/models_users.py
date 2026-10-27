# app/models/models_users.py
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True, index=True)
    nom: str
    email: str = Field(unique=True, index=True)
    age: int
    role: str = "user"
    is_active: bool = True