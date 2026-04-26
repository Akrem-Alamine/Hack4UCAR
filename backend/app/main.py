import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.limiter import limiter
from app.api.v1.router import api_router


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


app = FastAPI(
    title="UCAR — Plateforme de Gestion Universitaire",
    description="API de gestion intelligente multi-établissements",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
)

app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "UCAR API"}


@app.on_event("startup")
def check_security_config():
    weak_secrets = {
        "dev_secret_change_in_production",
        "change_me_in_production_use_openssl_rand_hex_32",
    }
    if settings.JWT_SECRET_KEY in weak_secrets or len(settings.JWT_SECRET_KEY) < 32:
        print(
            "\n[SECURITY WARNING] JWT_SECRET_KEY is weak or default!\n"
            "Run: openssl rand -hex 32\n"
            "Then set JWT_SECRET_KEY=<output> in your .env file.\n",
            file=sys.stderr,
        )


@app.on_event("startup")
def recover_stuck_jobs():
    """
    On every restart, any job left in 'processing' state was killed mid-flight.
    Re-queue them so they complete instead of hanging forever.
    """
    from app.core.database import SessionLocal
    from app.models.ingestion_job import IngestionJob, JobStatus

    db = SessionLocal()
    try:
        # Re-queue jobs stuck in 'processing' (killed mid-flight) and 'pending' document jobs
        stuck = db.query(IngestionJob).filter(
            IngestionJob.status.in_([JobStatus.processing, JobStatus.pending]),
            IngestionJob.source_type.in_(["pdf", "image"]),
        ).all()
        for job in stuck:
            job.status = JobStatus.pending
        if stuck:
            db.commit()
            print(f"[startup] Re-queueing {len(stuck)} unfinished document job(s).", file=sys.stderr)
            import threading
            from app.api.v1.ingestion import _process_document_job
            for job in stuck:
                if job.file_path:
                    from pathlib import Path
                    p = Path(job.file_path)
                    if p.exists():
                        file_bytes = p.read_bytes()
                        t = threading.Thread(
                            target=_process_document_job,
                            args=(job.id, file_bytes, job.original_filename),
                            daemon=True,
                        )
                        t.start()
                    else:
                        job.status = JobStatus.failed
                        job.error_message = "Fichier source introuvable après redémarrage."
            db.commit()
    finally:
        db.close()
