from fastapi import APIRouter
from app.api.v1 import auth, institutions, departments, kpis, alerts, reports, chat, ingestion, database_explorer

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(institutions.router)
api_router.include_router(departments.router)
api_router.include_router(kpis.router)
api_router.include_router(alerts.router)
api_router.include_router(reports.router)
api_router.include_router(chat.router)
api_router.include_router(ingestion.router)
api_router.include_router(database_explorer.router)
