from fastapi import APIRouter, Response
from http import HTTPStatus

router = APIRouter(tags=['Home'])

@router.get('/', status_code=HTTPStatus.OK, include_in_schema=False)
def root():
    return Response(content='API Electrolux e Novalar',status_code=HTTPStatus.OK)