from passlib.context import CryptContext

# Configura o contexto do passlib, especificando o algoritmo (bcrypt)
# e marcando esquemas obsoletos (se houver)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash bcrypt para uma senha."""
    return pwd_context.hash(password)
