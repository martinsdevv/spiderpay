import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# Propriedades compartilhadas por todos os schemas (evita repetição)
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email único do usuário")
    full_name: Optional[str] = Field(None, description="Nome completo do usuário")

# Schema para criação de usuário (recebido via API)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Senha do usuário (mínimo 8 caracteres)")

# Schema para atualização de usuário (campos opcionais)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

# Propriedades adicionais presentes no modelo do banco, mas não na criação
class UserInDBBase(UserBase):
    id: uuid.UUID
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Habilita o modo ORM para que o Pydantic possa ler dados
    # diretamente de objetos SQLAlchemy
    class Config:
        from_attributes = True

# Schema para retornar dados do usuário via API (exclui a senha)
class UserPublic(UserInDBBase):
    pass 

# Schema interno que inclui a senha (raramente exposto)
class User(UserInDBBase):
    hashed_password: str 