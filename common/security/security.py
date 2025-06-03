from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from http import HTTPStatus
from jwt import encode, decode, ExpiredSignatureError, DecodeError
from common.settings.settings import settings

# OAuth2 password flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

# Constantes
TIMEZONE = ZoneInfo('UTC')
ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
TOKEN_EXPIRE_HOURS = settings.ACCESS_TOKEN_EXPIRE_HOURS

def create_access_token(data: Dict[str, Any]) -> str:
    """Cria um token JWT assinado."""
    to_encode = data.copy()
    expire = datetime.now(tz=TIMEZONE) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    to_encode.update({'exp': expire})

    return encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def valid_token(token: str) -> Optional[str]:
    """Valida o token JWT e retorna o client_id (sub) se válido."""
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get('sub')
    except (ExpiredSignatureError, DecodeError):
        return None

def get_current_client(token: str = Depends(oauth2_scheme)) -> str:
    """Dependência do FastAPI para obter o client_id autenticado."""
    client_id = valid_token(token)
    if not client_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Token inválido ou expirado',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return client_id
