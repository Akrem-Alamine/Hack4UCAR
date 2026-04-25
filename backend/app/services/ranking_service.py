"""
Track 2 — Institution health index and ranking.
Computes a composite score 0-100 per institution based on KPI thresholds.
"""
from sqlalchemy.orm import Session
from app.models.kpi import KPIRecord
from app.models.institution import Institution

# KPI health configuration: (higher_is_better, ideal_value, worst_value, weight)
KPI_CONFIG: dict[str, tuple[bool, float, float, float]] = {
    # Academic
    "success_rate":          (True,  95.0,  40.0, 3.0),
    "dropout_rate":          (False,  2.0,  30.0, 3.0),
    "attendance_rate":       (True,  98.0,  50.0, 2.0),
    "repetition_rate":       (False,  3.0,  25.0, 1.5),
    # Finance
    "budget_execution_rate": (True,  95.0,  40.0, 2.0),
    "cost_per_student":      (False, 800.0, 5000.0, 1.0),
    # HR
    "absenteeism_rate":      (False,  2.0,  25.0, 2.0),
    "teaching_headcount":    (True,  50.0,   5.0, 1.0),
    "training_hours":        (True,  40.0,   0.0, 1.5),
    # ESG
    "energy_consumption_kwh":(False, 100.0, 2000.0, 1.5),
    "recycling_rate":        (True,  80.0,   0.0, 1.5),
    "carbon_footprint_ton":  (False,  5.0, 200.0, 1.0),
    # Insertion
    "employability_rate":    (True,  90.0,  30.0, 2.5),
    "insertion_delay_months":(False,  2.0,  18.0, 2.0),
    "national_convention_rate":(True, 80.0,  0.0, 1.0),
    # Research
    "publications_count":    (True,  30.0,   0.0, 1.5),
    "active_projects":       (True,  10.0,   0.0, 1.5),
    "funding_tnd":           (True, 500000, 0.0, 1.0),
}

DOMAIN_MAP: dict[str, str] = {
    "success_rate": "academic", "dropout_rate": "academic",
    "attendance_rate": "academic", "repetition_rate": "academic",
    "budget_execution_rate": "finance", "cost_per_student": "finance",
    "absenteeism_rate": "hr", "teaching_headcount": "hr", "training_hours": "hr",
    "energy_consumption_kwh": "esg", "recycling_rate": "esg", "carbon_footprint_ton": "esg",
    "employability_rate": "insertion", "insertion_delay_months": "insertion",
    "national_convention_rate": "insertion",
    "publications_count": "research", "active_projects": "research", "funding_tnd": "research",
}


def _kpi_score(indicator_key: str, value: float) -> float | None:
    cfg = KPI_CONFIG.get(indicator_key)
    if not cfg:
        return None
    higher_is_better, ideal, worst, _ = cfg
    if higher_is_better:
        raw = (value - worst) / (ideal - worst)
    else:
        raw = (worst - value) / (worst - ideal)
    return round(max(0.0, min(100.0, raw * 100)), 1)


def compute_institution_health(db: Session, institution_id: int) -> dict:
    """Compute the composite health index for one institution."""
    records = (
        db.query(KPIRecord)
        .filter(KPIRecord.institution_id == institution_id)
        .all()
    )

    # Keep only the latest record per indicator
    latest: dict[str, KPIRecord] = {}
    for r in sorted(records, key=lambda x: x.period_start):
        latest[r.indicator_key] = r

    domain_scores: dict[str, list[float]] = {}
    scored_kpis: list[dict] = []

    for indicator_key, record in latest.items():
        score = _kpi_score(indicator_key, record.value)
        if score is None:
            continue
        domain = DOMAIN_MAP.get(indicator_key, record.domain)
        domain_scores.setdefault(domain, []).append(score)
        scored_kpis.append({
            "indicator_key": indicator_key,
            "domain": domain,
            "value": record.value,
            "unit": record.unit,
            "score": score,
            "period_label": record.period_label,
        })

    per_domain = {
        domain: round(sum(scores) / len(scores), 1)
        for domain, scores in domain_scores.items()
    }

    overall = round(sum(per_domain.values()) / len(per_domain), 1) if per_domain else 0.0

    # Risk level
    if overall >= 75:
        risk = "low"
        risk_label = "Faible"
    elif overall >= 50:
        risk = "medium"
        risk_label = "Modéré"
    else:
        risk = "high"
        risk_label = "Élevé"

    return {
        "institution_id": institution_id,
        "overall_score": overall,
        "domain_scores": per_domain,
        "scored_kpis": scored_kpis,
        "risk_level": risk,
        "risk_label": risk_label,
        "kpi_count": len(scored_kpis),
    }


def get_institutions_ranking(db: Session) -> list[dict]:
    """Rank all active institutions by health index."""
    institutions = db.query(Institution).filter(Institution.is_active == True).all()

    ranking = []
    for inst in institutions:
        health = compute_institution_health(db, inst.id)
        ranking.append({
            "rank": 0,
            "institution_id": inst.id,
            "institution_name": inst.name,
            "institution_acronym": inst.acronym,
            "city": inst.city,
            "overall_score": health["overall_score"],
            "domain_scores": health["domain_scores"],
            "risk_level": health["risk_level"],
            "risk_label": health["risk_label"],
            "kpi_count": health["kpi_count"],
        })

    ranking.sort(key=lambda x: x["overall_score"], reverse=True)
    for i, item in enumerate(ranking):
        item["rank"] = i + 1

    return ranking
