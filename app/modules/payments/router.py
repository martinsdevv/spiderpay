import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .schema import PaymentCreate, PaymentUpdate, PaymentRead
from .service import PaymentService
from app.modules.users.models import User
from app.core.database import get_db_session 
from app.core.dependencies import get_current_active_user

router = APIRouter()
payment_service = PaymentService()

@router.post(
    "/", 
    response_model=PaymentRead, 
    status_code=status.HTTP_201_CREATED, 
    summary="Criar um novo pagamento"
)
async def create_payment(
    payment_in: PaymentCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Cria um novo registro de pagamento associado ao usuário autenticado.
    TODO: Associar ao usuário autenticado quando a autenticação for implementada.
    
    - **amount**: Valor do pagamento.
    - **currency**: Código da moeda (ex: BRL).
    - **description**: Descrição opcional.
    """
    # Usa o id do usuário obtido do token JWT
    return await payment_service.create_payment(
        db=db, payment_in=payment_in, user_id=current_user.id
    )

@router.get(
    "/", 
    response_model=List[PaymentRead],
    summary="Listar pagamentos"
)
async def read_payments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
): # O serviço será injetado ou usado diretamente
    """
    Retorna uma lista de pagamentos com paginação.
    TODO: Filtrar pagamentos apenas para o current_user?
    """
    payments = await payment_service.get_payments(db=db, skip=skip, limit=limit)
    # Lógica de filtro (exemplo):
    # payments = await payment_service.get_payments_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return payments

@router.get(
    "/{payment_id}", 
    response_model=PaymentRead,
    summary="Obter um pagamento pelo ID"
)
async def read_payment(
    payment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
): # O serviço será injetado ou usado diretamente
    """
    Retorna os detalhes de um pagamento específico pelo seu ID.
    """
    db_payment = await payment_service.get_payment(db=db, payment_id=payment_id)
    # Checagem de permissão: só o dono ou superuser pode ver
    if db_payment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado a ver este pagamento")
    return db_payment

@router.patch(
    "/{payment_id}", 
    response_model=PaymentRead,
    summary="Atualizar um pagamento (parcialmente)"
)
async def update_payment(
    payment_id: uuid.UUID,
    payment_in: PaymentUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
): # O serviço será injetado ou usado diretamente
    """
    Atualiza campos permitidos de um pagamento existente (ex: description).
    Utiliza PATCH para atualizações parciais.
    """
    # Busca inicial para verificar existência E PERMISSÃO
    db_payment = await payment_service.get_payment(db=db, payment_id=payment_id) 
    if db_payment.user_id != current_user.id and not current_user.is_superuser:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado a atualizar este pagamento")

    updated_payment = await payment_service.update_payment(
        db=db, payment_id=payment_id, payment_in=payment_in
    )
    return updated_payment
