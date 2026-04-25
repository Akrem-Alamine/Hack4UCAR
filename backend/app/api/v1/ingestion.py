"""
Track 1 — Data ingestion API.
Handles Excel/CSV (structured) and PDF/image (unstructured → OCR → AI extraction).
"""
import io
import os
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
import pandas as pd

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.kpi import KPIRecord
from app.models.department import Department
from app.models.ingestion_job import IngestionJob, JobStatus, JobSourceType
from app.dependencies.auth import get_current_user, get_scoped_institution_id

router = APIRouter(prefix="/ingestion", tags=["Import de données"])

REQUIRED_COLS = {"domain", "indicator_key", "value", "unit", "period_label", "period_start", "period_end"}

DOMAIN_ALIASES = {
    "academique": "academic", "académique": "academic",
    "finance": "finance", "financier": "finance",
    "rh": "hr", "ressources humaines": "hr", "ressources_humaines": "hr",
    "esg": "esg", "rse": "esg",
    "insertion": "insertion", "insertion professionnelle": "insertion",
    "recherche": "research", "research": "research",
    "infrastructure": "infrastructure",
    "partenariats": "partnerships", "partnerships": "partnerships",
    "vie estudiantine": "student_life", "student_life": "student_life",
}

UNSTRUCTURED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif", ".webp"}

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB

# Allowed magic byte signatures per extension (None = text file, skip check)
_MAGIC: dict[str, tuple[bytes, ...] | None] = {
    ".xlsx": (b"PK\x03\x04",),
    ".xls": (b"\xd0\xcf\x11\xe0",),
    ".csv": None,
    ".pdf": (b"%PDF",),
    ".png": (b"\x89PNG",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".tiff": (b"II*\x00", b"MM\x00*"),
    ".bmp": (b"BM",),
    ".gif": (b"GIF87a", b"GIF89a"),
    ".webp": (b"RIFF",),
}


def _validate_magic(content: bytes, ext: str) -> bool:
    expected = _MAGIC.get(ext)
    if expected is None:
        return True
    return any(content.startswith(m) for m in expected)


def _parse_date(val) -> date:
    if isinstance(val, (date, datetime)):
        return val.date() if isinstance(val, datetime) else val
    s = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Format de date non reconnu : {val!r}")


def _normalize_domain(raw: str) -> str:
    return DOMAIN_ALIASES.get(raw.strip().lower(), raw.strip().lower())


def _ai_normalize_dataframe(df: "pd.DataFrame") -> "tuple[pd.DataFrame, bool]":
    """
    When the Excel/CSV columns don't match the required format, use Groq to:
    1. Map existing columns to the standard schema
    2. Extract KPI rows if the file is in a report/narrative style
    Returns (normalized_df, was_ai_used).
    """
    import json, re
    from groq import Groq
    from app.core.config import settings

    client = Groq(api_key=settings.GROQ_API_KEY)

    cols = df.columns.tolist()
    sample = df.head(5).to_dict(orient="records")

    prompt = f"""Tu es un expert en normalisation de données universitaires.

Voici un fichier Excel/CSV avec les colonnes suivantes:
{cols}

Et voici les 5 premières lignes:
{json.dumps(sample, ensure_ascii=False, default=str)}

Ta mission: mapper ces données vers le format standard suivant et retourner UN TABLEAU JSON de lignes normalisées.

Format standard requis pour chaque ligne:
{{
  "domain": "academic|finance|hr|esg|insertion|research",
  "indicator_key": "snake_case_key",
  "value": 12.5,
  "unit": "%|TND|nombre|kWh|mois",
  "period_label": "2024-2025 S1",
  "period_start": "2024-09-01",
  "period_end": "2025-01-31"
}}

Règles:
- Infère le domaine depuis le nom de l'indicateur si non précisé
- Génère des dates cohérentes si absentes (utilise 2024-01-01 / 2024-12-31 par défaut)
- Convertis les % implicites (ex: "82%" → value=82, unit="%")
- indicator_key doit être en snake_case sans accents
- Retourne UNIQUEMENT le tableau JSON, rien d'autre

Traite TOUTES les lignes du fichier (pas seulement les 5 premières).
Données complètes:
{json.dumps(df.to_dict(orient="records"), ensure_ascii=False, default=str)[:4000]}
"""

    try:
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=3000,
        )
        raw = completion.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        rows = json.loads(raw)
        if not isinstance(rows, list) or len(rows) == 0:
            return df, False
        import pandas as pd
        normalized = pd.DataFrame(rows)
        normalized.columns = [c.strip().lower() for c in normalized.columns]
        return normalized, True
    except Exception:
        return df, False


def _save_upload(file_bytes: bytes, filename: str, institution_id: int) -> str:
    uploads_dir = Path(settings.UPLOADS_DIR) / str(institution_id)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{ts}_{Path(filename).name}"
    dest = uploads_dir / safe_name
    dest.write_bytes(file_bytes)
    return str(dest)


# ─── Excel / CSV import ───────────────────────────────────────────────────────

@router.post("/upload")
async def upload_kpi_file(
    file: UploadFile = File(...),
    institution_id: int = Form(...),
    period_label_override: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_id = get_scoped_institution_id(institution_id, current_user)
    if not scoped_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cet établissement")

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 50 Mo)")

    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    # Route unstructured files to the AI pipeline
    if ext in UNSTRUCTURED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail="Utilisez /ingestion/upload-document pour les fichiers PDF et images."
        )

    if not _validate_magic(content, ext):
        raise HTTPException(status_code=422, detail="Le contenu du fichier ne correspond pas à son extension déclarée")

    try:
        df = pd.read_csv(io.BytesIO(content)) if ext == ".csv" else pd.read_excel(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Impossible de lire le fichier. Vérifiez le format et réessayez.")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    missing = REQUIRED_COLS - set(df.columns)

    # If columns don't match, try AI-assisted normalization
    ai_normalized = False
    if missing:
        df, ai_normalized = _ai_normalize_dataframe(df)
        missing = REQUIRED_COLS - set(df.columns)

    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Colonnes manquantes même après normalisation IA : {', '.join(sorted(missing))}. "
                   f"Colonnes reçues : {', '.join(df.columns.tolist())}",
        )

    dept_cache: dict[str, int] = {}
    errors: list[dict] = []
    imported: list[dict] = []

    for row_idx, row in df.iterrows():
        row_num = int(row_idx) + 2
        try:
            value = float(row["value"])
        except (ValueError, TypeError):
            errors.append({"row": row_num, "error": f"Valeur invalide : {row.get('value')}"})
            continue
        try:
            period_start = _parse_date(row["period_start"])
            period_end = _parse_date(row["period_end"])
        except ValueError as e:
            errors.append({"row": row_num, "error": str(e)})
            continue

        domain = _normalize_domain(
            current_user.domain_scope if current_user.domain_scope else str(row.get("domain", ""))
        )
        indicator_key = str(row.get("indicator_key", "")).strip().lower().replace(" ", "_")
        unit = str(row.get("unit", "")).strip()
        period_label = period_label_override or str(row.get("period_label", "")).strip()
        notes = str(row.get("notes", "")).strip() if "notes" in df.columns else None

        dept_id: Optional[int] = None
        if "department_code" in df.columns and pd.notna(row.get("department_code")):
            code = str(row["department_code"]).strip()
            if code not in dept_cache:
                dept = db.query(Department).filter(
                    Department.institution_id == scoped_id,
                    Department.code == code,
                ).first()
                dept_cache[code] = dept.id if dept else -1
            dept_id = dept_cache[code] if dept_cache[code] != -1 else None

        db.add(KPIRecord(
            institution_id=scoped_id, department_id=dept_id,
            domain=domain, indicator_key=indicator_key,
            value=value, unit=unit, period_label=period_label,
            period_start=period_start, period_end=period_end,
            notes=notes or None, created_by=current_user.id,
        ))
        imported.append({"row": row_num, "domain": domain, "indicator_key": indicator_key, "value": value, "unit": unit})

    db.commit()
    msg = f"{len(imported)} indicateur(s) importé(s), {len(errors)} erreur(s)."
    if ai_normalized:
        msg = f"[IA] Colonnes normalisées automatiquement. " + msg
    return {
        "imported": len(imported), "errors": len(errors),
        "ai_normalized": ai_normalized,
        "rows": imported[:20], "error_details": errors,
        "message": msg,
    }


# ─── PDF / Image AI extraction ────────────────────────────────────────────────

@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    institution_id: int = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Track 1: Upload a PDF or image. Runs OCR + AI extraction asynchronously.
    Returns a job ID to poll for status.
    """
    scoped_id = get_scoped_institution_id(institution_id, current_user)
    if not scoped_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cet établissement")

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 50 Mo)")

    filename = file.filename or "document"
    ext = Path(filename).suffix.lower()

    if not _validate_magic(content, ext):
        raise HTTPException(status_code=422, detail="Le contenu du fichier ne correspond pas à son extension déclarée")

    if ext == ".pdf":
        source_type = JobSourceType.pdf
    elif ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif", ".webp"}:
        source_type = JobSourceType.image
    else:
        raise HTTPException(status_code=422, detail=f"Format non supporté : {ext}. Acceptés: PDF, PNG, JPG, TIFF")

    file_path = _save_upload(content, filename, scoped_id)

    job = IngestionJob(
        institution_id=scoped_id,
        created_by=current_user.id,
        source_type=source_type,
        original_filename=filename,
        file_path=file_path,
        status=JobStatus.pending,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(_process_document_job, job.id, content, filename)

    return {
        "job_id": job.id,
        "status": "pending",
        "message": "Document reçu. Extraction IA en cours...",
        "filename": filename,
    }


def _process_document_job(job_id: int, file_bytes: bytes, filename: str):
    """Background task: OCR → AI extraction → save KPIs."""
    from app.core.database import SessionLocal
    from app.ingestion.pdf_extractor import extract_text
    from app.ingestion.ai_extractor import extract_kpis_from_text, validate_extracted_kpis

    db = SessionLocal()
    try:
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if not job:
            return

        job.status = JobStatus.processing
        db.commit()

        # Step 1: Extract text via OCR/pdfplumber
        text, method = extract_text(file_bytes, filename)
        job.extracted_text = text[:10000] if text else ""

        if not text:
            job.status = JobStatus.failed
            job.error_message = "Impossible d'extraire du texte du document."
            db.commit()
            return

        # Step 2: AI KPI extraction
        kpis = extract_kpis_from_text(text)
        job.extracted_kpis = kpis
        job.kpi_count = len(kpis)

        # Step 3: Quality validation
        validation = validate_extracted_kpis(kpis)
        job.quality_score = validation.get("quality_score", 0)

        # Step 4: Save high-confidence KPIs to database
        imported = 0
        today = date.today()
        for kpi in kpis:
            if kpi.get("confidence", 0) < 0.5:
                continue
            try:
                period_label = kpi.get("period_label", "Document importé")
                if period_label == "N/A":
                    period_label = "Document importé"

                db.add(KPIRecord(
                    institution_id=job.institution_id,
                    created_by=job.created_by,
                    domain=_normalize_domain(kpi["domain"]),
                    indicator_key=kpi["indicator_key"].strip().lower().replace(" ", "_"),
                    value=float(kpi["value"]),
                    unit=kpi.get("unit", ""),
                    period_label=period_label,
                    period_start=today,
                    period_end=today,
                    notes=f"Extrait automatiquement depuis {filename}",
                ))
                imported += 1
            except Exception:
                continue

        db.commit()
        job.imported_count = imported
        job.status = JobStatus.completed
        job.completed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        if job:
            job.status = JobStatus.failed
            job.error_message = str(e)[:500]
            db.commit()
    finally:
        db.close()


# ─── Job status / listing ─────────────────────────────────────────────────────

@router.get("/jobs")
def list_jobs(
    institution_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_id = get_scoped_institution_id(institution_id, current_user)
    query = db.query(IngestionJob)
    if scoped_id:
        query = query.filter(IngestionJob.institution_id == scoped_id)
    jobs = query.order_by(IngestionJob.created_at.desc()).limit(50).all()
    return [_job_to_dict(j) for j in jobs]


@router.get("/jobs/{job_id}")
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    if current_user.role.value != "super_admin" and job.institution_id != current_user.institution_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    return _job_to_dict(job, include_text=True)


@router.post("/jobs/{job_id}/confirm")
def confirm_job_kpis(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually trigger import of extracted KPIs that were pending confirmation."""
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    if job.status != JobStatus.completed:
        raise HTTPException(status_code=400, detail="La tâche n'est pas encore complétée")

    return {"message": f"{job.imported_count} KPIs déjà importés lors de l'extraction initiale."}


@router.get("/template")
def download_template():
    return {
        "columns": list(REQUIRED_COLS) + ["department_code", "notes"],
        "example_row": {
            "domain": "academic",
            "indicator_key": "success_rate",
            "value": 82.5,
            "unit": "%",
            "period_label": "2024-2025 S1",
            "period_start": "2024-09-01",
            "period_end": "2025-01-31",
            "department_code": "INFO",
            "notes": "Données validées par le service scolarité",
        },
        "domain_values": list(set(DOMAIN_ALIASES.values())),
        "supported_formats": ["xlsx", "xls", "csv", "pdf", "png", "jpg", "jpeg"],
    }


def _job_to_dict(job: IngestionJob, include_text: bool = False) -> dict:
    d = {
        "id": job.id,
        "institution_id": job.institution_id,
        "source_type": job.source_type.value,
        "original_filename": job.original_filename,
        "status": job.status.value,
        "kpi_count": job.kpi_count,
        "quality_score": job.quality_score,
        "imported_count": job.imported_count,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "extracted_kpis": job.extracted_kpis or [],
    }
    if include_text:
        d["extracted_text"] = (job.extracted_text or "")[:2000]
    return d
