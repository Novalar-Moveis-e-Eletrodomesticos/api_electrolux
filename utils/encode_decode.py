from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from common.settings.settings import settings

pwd_context = CryptContext(schemes=[settings.SCHEMES], deprecated=settings.DEPRECATED)

def validar_senha(pw, hh):
    try:
        return pwd_context.verify(pw, hh)
    except UnknownHashError:
        return False

def criar_hash(senha):
    if not senha:
        return {
            'retorno': "Senha inválida",
            'status': False
        }
    try:
        hash_gerado = pwd_context.hash(senha)
        return {
            'retorno': hash_gerado,
            'status': True
        }
    except Exception as e:
        return {
            'retorno': f"Erro ao criar o hash: {e}",
            'status': False
        }