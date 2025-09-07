from fastapi import FastAPI
from .api.v1 import endpoints
from .core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(endpoints.router, prefix="/api/v1")


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Homelab API"}
