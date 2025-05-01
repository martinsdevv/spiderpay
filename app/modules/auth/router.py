from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import create_access_token, verify_password
from app.modules.users import service as user_service
from .schema import Token, LoginRequest

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Incorrect username or password"}}
)

@router.post("/login", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtém um token JWT fornecendo email e senha em JSON."""
    user = await user_service.get_user_by_email(db, email=login_data.email)
    
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"} 