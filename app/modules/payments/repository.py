import uuid
from typing import Sequence, Any, Dict, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Payment, PaymentStatus
from .schema import PaymentCreate, PaymentUpdate


class PaymentRepository:
    async def create(
        self, 
        db: AsyncSession, 
        *, 
        payment_in: PaymentCreate, 
        user_id: uuid.UUID, 
        gateway: str
    ) -> Payment:
        """Cria um novo registro de pagamento no banco."""
        db_payment = Payment(
            **payment_in.model_dump(),
            user_id=user_id,
            gateway=gateway,
            status=PaymentStatus.PENDING # Status inicial
        )
        db.add(db_payment)
        await db.commit()
        await db.refresh(db_payment)
        return db_payment

    async def get_by_id(self, db: AsyncSession, payment_id: uuid.UUID) -> Payment | None:
        """Busca um pagamento pelo seu ID."""
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> Sequence[Payment]:
        """Busca múltiplos pagamentos com paginação básica."""
        stmt = select(Payment).offset(skip).limit(limit).order_by(Payment.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
        
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_payment: Payment, 
        payment_in: PaymentUpdate | Dict[str, Any]
    ) -> Payment:
        """Atualiza um registro de pagamento existente."""
        if isinstance(payment_in, dict):
            update_data = payment_in
        else:
            # Exclui valores não definidos para permitir atualizações parciais (PATCH)
            update_data = payment_in.model_dump(exclude_unset=True)

        # Atualiza os atributos do objeto SQLAlchemy existente
        for field, value in update_data.items():
            setattr(db_payment, field, value)

        db.add(db_payment)
        await db.commit()
        await db.refresh(db_payment)
        return db_payment
        
    async def update_status(
        self,
        db: AsyncSession,
        *,
        db_payment: Payment,
        new_status: PaymentStatus,
        gateway_payment_id: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Payment:
        """Atualiza especificamente o status e informações relacionadas do gateway."""
        db_payment.status = new_status
        if gateway_payment_id is not None:
             db_payment.gateway_payment_id = gateway_payment_id
        if error_message is not None:
             db_payment.error_message = error_message
             
        db.add(db_payment)
        await db.commit()
        await db.refresh(db_payment)
        return db_payment
