"""
Database explorer API — read-only SGBD-style navigation.
Super admin only.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/db-explorer", tags=["Base de données"])

_SUPER_ADMIN_ONLY = "Accès réservé au super administrateur"

# Tables exposed for browsing — explicit allowlist for security
ALLOWED_TABLES = {
    "institutions", "users", "kpi_records", "alert_rules", "alerts",
    "reports", "ingestion_jobs", "departments",
}


def _require_super_admin(user: User):
    if user.role.value != "super_admin":
        raise HTTPException(status_code=403, detail=_SUPER_ADMIN_ONLY)


@router.get("/tables")
def list_tables(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_super_admin(current_user)
    inspector = inspect(db.bind)
    all_tables = inspector.get_table_names()
    result = []
    for table in sorted(all_tables):
        if table not in ALLOWED_TABLES:
            continue
        count_row = db.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar()
        columns = [
            {"name": col["name"], "type": str(col["type"])}
            for col in inspector.get_columns(table)
        ]
        result.append({"name": table, "row_count": count_row, "columns": columns})
    return result


@router.get("/tables/{table_name}/rows")
def get_rows(
    table_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    sort_col: Optional[str] = Query(None),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_super_admin(current_user)

    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=404, detail="Table non autorisée")

    inspector = inspect(db.bind)
    columns = [col["name"] for col in inspector.get_columns(table_name)]

    # Validate sort column
    if sort_col and sort_col not in columns:
        sort_col = None
    order_clause = ""
    if sort_col:
        order_clause = f'ORDER BY "{sort_col}" {sort_dir.upper()}'
    elif "id" in columns:
        order_clause = f"ORDER BY id {sort_dir.upper()}"

    # Optional full-text search across all text columns
    where_clause = ""
    params: dict = {}
    if search and search.strip():
        text_cols = [
            col["name"]
            for col in inspector.get_columns(table_name)
            if "CHAR" in str(col["type"]).upper()
            or "TEXT" in str(col["type"]).upper()
        ]
        if text_cols:
            conditions = " OR ".join(
                f'CAST("{c}" AS TEXT) ILIKE :search' for c in text_cols
            )
            where_clause = f"WHERE {conditions}"
            params["search"] = f"%{search.strip()}%"

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    count_sql = text(f'SELECT COUNT(*) FROM "{table_name}" {where_clause}')
    total = db.execute(count_sql, params).scalar()

    rows_sql = text(
        f'SELECT * FROM "{table_name}" {where_clause} {order_clause} LIMIT :limit OFFSET :offset'
    )
    rows = db.execute(rows_sql, params).mappings().all()

    return {
        "table": table_name,
        "columns": columns,
        "rows": [dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": max(1, (total + page_size - 1) // page_size),
    }


@router.get("/tables/{table_name}/row/{row_id}")
def get_row(
    table_name: str,
    row_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_super_admin(current_user)
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=404, detail="Table non autorisée")

    row = db.execute(
        text(f'SELECT * FROM "{table_name}" WHERE id = :id'), {"id": row_id}
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
    return dict(row)
