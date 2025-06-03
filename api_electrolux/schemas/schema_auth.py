from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SchemaAuth(BaseModel):
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
