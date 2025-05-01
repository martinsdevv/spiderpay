from fastapi import FastAPI
from app.core.config import settings
from app.modules.users import router as users_router
app = FastAPI(
    title=settings.APP_NAME,
    description="API de Pagamentos Simulada - Projeto de Portfólio",
    version="0.1.0",
)

# Inclui o router do módulo de usuários na aplicação principal
app.include_router(users_router.router)


# Endpoint raiz opcional para verificação
@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint raiz da API."""
    return {"message": f"Welcome to {settings.APP_NAME}"}
