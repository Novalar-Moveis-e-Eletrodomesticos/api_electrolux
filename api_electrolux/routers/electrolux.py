from fastapi import APIRouter, HTTPException, Depends
from http import HTTPStatus
from typing import List
from api_electrolux.schemas.schema_electrolux import (
    SchemaElectrolux, SchemaElectroluxGet, SchemaElectroluxGetModel
)
from common.db.db import db
from common.security.security import get_current_client

router = APIRouter(tags=['Electrolux'], prefix='/consulta')

# Constantes de configuração
ID_LOCAL_SALDO = [1, 2, 3, 5, 6, 44, 99]
MARCA_ELECTROLUX = 60

def executar_consulta(params: dict, arquivo: str, base: str = 'sabium'):
    try:
        resultados = db.consulta(params=params, arquivo=arquivo, base=base)
        return resultados
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao processar a consulta: {str(e)}"
        )

@router.post('/electrolux',status_code=HTTPStatus.OK,response_model=SchemaElectroluxGet)
def consultar_dados_electrolux(payload: SchemaElectrolux,client_id: str = Depends(get_current_client)):
    # Consulta filiais
    filiais_resultado = executar_consulta(params={}, arquivo='filiais.sql')
    
    if not filiais_resultado:
        raise HTTPException(status_code=HTTPStatus.NO_CONTENT, detail="Nenhuma filial encontrada.")

    filiais = [fil[0] for fil in filiais_resultado]

    # Parâmetros para consulta principal
    query_params = {
        'data_ini': payload.data_inicial,
        'data_fin': payload.data_final,
        'filial': filiais,
        'idlocalsaldo': ID_LOCAL_SALDO,
        'marca': MARCA_ELECTROLUX
    }

    resultados = executar_consulta(params=query_params, arquivo='electrolux.sql')

    if not resultados:
        raise HTTPException(status_code=HTTPStatus.NO_CONTENT, detail="Nenhum dado encontrado.")

    dados: List[SchemaElectroluxGetModel] = [
        SchemaElectroluxGetModel(
            data_sell_out=row[0],
            cnpj=row[1],
            tipo_cnpj=row[2],
            ean=row[3],
            quantidade=row[4],
            estoque=row[5]
        )
        for row in resultados
    ]

    return SchemaElectroluxGet(resultado=dados)
