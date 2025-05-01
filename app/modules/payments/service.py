import uuid
from typing import Sequence, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from .models import Payment
from .repository import PaymentRepository
from .schema import PaymentCreate, PaymentUpdate


class PaymentService:
    def __init__(self, repository: PaymentRepository = PaymentRepository()):
        self.repository = repository

    async def create_payment(
        self, 
        db: AsyncSession, 
        *, 
        payment_in: PaymentCreate, 
        user_id: uuid.UUID
    ) -> Payment:
        """Cria um novo pagamento."""
        # Obtém o gateway ativo da configuração
        active_gateway = settings.ACTIVE_GATEWAY
        
        # Chama o repositório para criar o pagamento no banco
        db_payment = await self.repository.create(
            db,
            payment_in=payment_in,
            user_id=user_id,
            gateway=active_gateway
        )
        
        # TODO: Lógica futura - Chamar o GatewayService para iniciar o pagamento externo
        # gateway_service = get_gateway_service() # Obter instância do serviço do gateway
        # try:
        #     gateway_response = await gateway_service.initiate_payment(payment_id=db_payment.id, amount=db_payment.amount, ...)
        #     # Atualizar status/gateway_id com base na resposta
        #     await self.repository.update_status(db, db_payment=db_payment, new_status=PaymentStatus.PROCESSING, gateway_payment_id=gateway_response.id)
        # except GatewayError as e:
        #     # Atualizar status para FAILED e registrar erro
        #     await self.repository.update_status(db, db_payment=db_payment, new_status=PaymentStatus.FAILED, error_message=str(e))
        #     # Relançar ou tratar o erro conforme necessário
        
        return db_payment

    async def get_payment(self, db: AsyncSession, payment_id: uuid.UUID) -> Payment:
        """Busca um pagamento pelo ID. Lança exceção se não encontrado."""
        db_payment = await self.repository.get_by_id(db, payment_id)
        if not db_payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pagamento não encontrado",
            )
        return db_payment

    async def get_payments(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> Sequence[Payment]:
        """Busca múltiplos pagamentos."""
        return await self.repository.get_multi(db, skip=skip, limit=limit)
        
    async def update_payment(
        self, 
        db: AsyncSession, 
        *, 
        payment_id: uuid.UUID,
        payment_in: PaymentUpdate
    ) -> Payment:
        """Atualiza um pagamento existente (apenas campos permitidos)."""
        db_payment = await self.get_payment(db, payment_id) # Reusa get_payment para buscar e tratar 404
        
        # Verifica se há dados para atualizar
        update_data = payment_in.model_dump(exclude_unset=True)
        if not update_data:
            # Se nada foi enviado no PATCH, apenas retorna o objeto existente
            return db_payment
            
        return await self.repository.update(
            db, db_payment=db_payment, payment_in=update_data
        )

    # TODO: Adicionar métodos para lidar com respostas do gateway (webhooks?)
    # async def handle_gateway_update(self, db: AsyncSession, gateway_payload: Dict) -> None:
    #     gateway_payment_id = gateway_payload.get("id")
    #     # Buscar pagamento pelo gateway_payment_id
    #     # Atualizar status usando self.repository.update_status
    #     pass
