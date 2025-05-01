import uuid
import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    String,
    Numeric,
    DateTime,
    func,
    Enum as SQLAlchemyEnum,
    JSON 
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB 

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.users.models import User # Evita importação circular

# Estados possíveis para um pagamento
class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    APPROVED = "APPROVED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    REFUNDED = "REFUNDED"
    CHARGEBACK = "CHARGEBACK"

class Payment(Base):
    __tablename__ = "payments"

    # Identificador único do pagamento em nosso sistema
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Chave estrangeira para o usuário que iniciou o pagamento
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    # Valor monetário do pagamento (precisão é importante)
    amount: Mapped[Numeric] = mapped_column(Numeric(10, 2))
    # Código da moeda ISO 4217
    currency: Mapped[str] = mapped_column(String(3)) 
    # Status atual do pagamento
    status: Mapped[PaymentStatus] = mapped_column(
        SQLAlchemyEnum(PaymentStatus), default=PaymentStatus.PENDING, index=True
    )
    # Descrição opcional para o pagamento
    description: Mapped[str | None] = mapped_column(String)
    # Identificador do gateway de pagamento utilizado
    gateway: Mapped[str] = mapped_column(String(50))
    # ID único atribuído pelo gateway de pagamento externo
    gateway_payment_id: Mapped[str | None] = mapped_column(String, index=True)
    # Mensagem de erro do gateway, se houver
    error_message: Mapped[str | None] = mapped_column(String)
    # Campo flexível para dados adicionais específicos do gateway/aplicação
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSONB 
    )
    # Timestamp da criação do registro
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Timestamp da última atualização do registro
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamento com o modelo User
    user: Mapped["User"] = relationship(back_populates="payments")
