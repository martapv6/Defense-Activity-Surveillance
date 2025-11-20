from pydantic import BaseModel, EmailStr, ConfigDict
from src.schemas.role import UserRole # The Enum we defined for validation
from datetime import datetime

# --- Base Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None

# --- Input Schemas ---
class UserCreate(UserBase):
    password: str

# --- Output Schemas --- asta ar fi utila pt frontend - in momentul in care user-ul e creat sa i se afiseze datele undeva
class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True) # Enables ORM mode for SQLAlchemy models
    
    id: int
    role_name: UserRole
    is_active: bool
    created_at: datetime
    
# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: str | None = None