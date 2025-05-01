import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict
from .models import PaymentStatus


# Schema base com campos comuns
class PaymentBase(BaseModel):
    amount: Decimal = Field(..., max_digits=10, decimal_places=2, gt=0)
    currency: str = Field(..., min_length=3, max_length=3) # Ex: "BRL"
    description: Optional[str] = None


# Usado para criar um pagamento. user_id virá do contexto de autenticação.
class PaymentCreate(PaymentBase):
    pass


# Usado para atualizar pagamento via PATCH. Apenas campos permitidos.
class PaymentUpdate(BaseModel):
    description: Optional[str] = None


# Usado para retornar dados do pagamento na API.
class PaymentRead(PaymentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: PaymentStatus
    gateway: str
    gateway_payment_id: Optional[str] = None
    error_message: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="additional_data") 
    created_at: datetime
    updated_at: datetime

    # Habilita leitura de atributos do modelo ORM
    model_config = ConfigDict(from_attributes=True)

    # Remapear metadata_ para metadata na saída (opcional, mas comum)
    # Pydantic v2 usa serialization_alias ou alias diretamente
    # O alias em metadata_ já deve cuidar disso na serialização se from_attributes=True estiver ativo.
    # Se não funcionar, podemos usar um @computed_field ou root_validator/model_validator.
    # Vamos manter simples por agora com o alias.
