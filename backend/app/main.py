from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, SessionLocal, engine
from .routers import dashboard, energy, health
from .simulation import seed_database

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_database(db)

app = FastAPI(title="VoltSense AI", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(energy.router)
