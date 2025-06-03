from fastapi import FastAPI
from api_electrolux.routers import (
    home,
    electrolux,
    auth
)

app = FastAPI(
    title="API Electrolux",version="0.0.1"
)

app.include_router(auth.router)
app.include_router(electrolux.router)
app.include_router(home.router)