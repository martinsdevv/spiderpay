from fastapi import FastAPI
from app.core.config import settings
from app.modules.users import router as users_router
from app.modules.payments import router as payments_router
from app.modules.auth import router as auth_router

app = FastAPI(
    title=settings.APP_NAME,
    description="API de Pagamentos Simulada - Projeto de Portfólio",
    version="0.1.0",
)

app.include_router(users_router.router, prefix="/users", tags=["Users"])
app.include_router(payments_router.router, prefix="/payments", tags=["Payments"])
app.include_router(auth_router.router)

@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint raiz da API."""
    return {"message": f"Welcome to {settings.APP_NAME}"}
