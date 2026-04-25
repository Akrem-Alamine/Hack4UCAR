"""
Excel / CSV ingestion endpoint.

Expected Excel format (one sheet, any name):
| domain | indicator_key | value | unit | period_label | period_start | period_end | department_code (optional) | notes (optional) |

period_start / period_end accept: YYYY-MM-DD or DD/MM/YYYY
"""
import io
from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from app.core.database import get_db
from app.models.user import User
from app.models.kpi import KPIRecord
from app.models.department import Department
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
    key = raw.strip().lower()
    return DOMAIN_ALIASES.get(key, key)


@router.post("/upload")
async def upload_kpi_file(
    file: UploadFile = File(...),
    institution_id: int = Form(...),
    period_label_override: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload an Excel (.xlsx) or CSV file with KPI data for one institution.
    Returns a preview of imported rows and any validation errors.
    """
    scoped_id = get_scoped_institution_id(institution_id, current_user)
    if not scoped_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cet établissement")

    content = await file.read()
    filename = file.filename or ""

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Impossible de lire le fichier : {e}")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Colonnes manquantes : {', '.join(sorted(missing))}. "
                   f"Colonnes reçues : {', '.join(df.columns.tolist())}",
        )

    dept_cache: dict[str, int] = {}
    errors: list[dict] = []
    imported: list[dict] = []

    for row_idx, row in df.iterrows():
        row_num = int(row_idx) + 2  # 1-based + header row

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

        # Department users are locked to their domain scope; others read from file
        domain = _normalize_domain(
            current_user.domain_scope if current_user.domain_scope
            else str(row.get("domain", ""))
        )
        indicator_key = str(row.get("indicator_key", "")).strip().lower().replace(" ", "_")
        unit = str(row.get("unit", "")).strip()
        period_label = period_label_override or str(row.get("period_label", "")).strip()
        notes = str(row.get("notes", "")).strip() if "notes" in df.columns else None

        # Resolve optional department
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

        record = KPIRecord(
            institution_id=scoped_id,
            department_id=dept_id,
            domain=domain,
            indicator_key=indicator_key,
            value=value,
            unit=unit,
            period_label=period_label,
            period_start=period_start,
            period_end=period_end,
            notes=notes or None,
            created_by=current_user.id,
        )
        db.add(record)
        imported.append({
            "row": row_num,
            "domain": domain,
            "indicator_key": indicator_key,
            "value": value,
            "unit": unit,
            "period_label": period_label,
            "department_code": row.get("department_code") if "department_code" in df.columns else None,
        })

    db.commit()

    return {
        "imported": len(imported),
        "errors": len(errors),
        "rows": imported[:20],  # preview first 20
        "error_details": errors,
        "message": f"{len(imported)} indicateur(s) importé(s) avec succès, {len(errors)} erreur(s).",
    }


@router.get("/template")
def download_template():
    """Returns the expected column names and an example row."""
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
        "notes": (
            "Les colonnes domain et indicator_key sont libres mais doivent être cohérentes. "
            "department_code est optionnel — il doit correspondre au code d'un département existant. "
            "Formats de date acceptés: YYYY-MM-DD ou DD/MM/YYYY."
        ),
    }
