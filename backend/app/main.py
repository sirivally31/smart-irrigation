from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import initialize_database
from app.routers.readings import router as readings_router
from app.routers.configuration import router as configuration_router
from app.routers.weather import router as weather_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Smart Irrigation API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_methods=["*"], allow_headers=["*"])
app.include_router(readings_router)
app.include_router(configuration_router)
app.include_router(weather_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}