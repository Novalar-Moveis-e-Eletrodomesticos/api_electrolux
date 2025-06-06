from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from http import HTTPStatus
from typing import Annotated
from common.security.security import create_access_token
from api_electrolux.schemas.schema_auth import SchemaAuth, TokenResponse
from common.db.db import db

T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
router = APIRouter(prefix='/auth', tags=['Auth'])

def consultar_cliente(client_id: str):
    """Consulta o cliente no banco de dados."""
    sql_file = 'valida_client.sql'
    query_params = {'idclient': client_id}
    try:
        resultados = db.consulta(params=query_params, arquivo=sql_file, base='dw')
        return resultados
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar cliente: {str(e)}"
        )

@router.post('/login', response_model=TokenResponse, status_code=HTTPStatus.OK)
def login(login: T_OAuth2Form):
    resultados = consultar_cliente(login.username)

    if not resultados:
        raise HTTPException(
            status_code=HTTPStatus.NO_CONTENT,
            detail='Cliente não encontrado'
        )
    
    row = resultados[0]

    try:
        db_client_secret = row[1]
        db_client_name = row[2]
    except IndexError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Formato inesperado de retorno da consulta'
        )

    if db_client_secret != login.password:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Credenciais inválidas'
        )

    token_data = {
        "sub": login.username,
        "name": db_client_name
    }

    token = create_access_token(data=token_data)

    return TokenResponse(access_token=token)
