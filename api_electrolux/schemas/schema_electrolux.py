from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date


class SchemaElectrolux(BaseModel):
    data_inicial: Optional[date] = None
    data_final: Optional[date] = None

    @field_validator("data_final")
    def check_date_range(cls, v, info):
        data_inicial = info.data.get("data_inicial")
        if v and data_inicial and v < data_inicial:
            raise ValueError("data_final não pode ser anterior à data_inicial")
        return v

class SchemaElectroluxGetModel(BaseModel):
    data_sell_out: Optional[date] = None
    cnpj: Optional[str] = None
    tipo_cnpj: Optional[str] = None
    ean: Optional[str] = None
    quantidade: Optional[int] = None
    estoque: Optional[int] = None

class SchemaElectroluxGet(BaseModel):
    resultado: List[SchemaElectroluxGetModel]
