"""
Track 1 — AI-powered KPI extraction from unstructured text.
Uses Groq to identify and structure KPI data from OCR/PDF text.
"""
import json
import re
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

EXTRACTION_PROMPT = """Tu es un expert en analyse de données universitaires.
Extrais UNIQUEMENT les indicateurs de performance (KPIs) explicitement chiffrés dans le texte suivant.

Indicateurs acceptés — utilise EXACTEMENT ces indicator_key:
Académique : success_rate, attendance_rate, dropout_rate, repetition_rate, enrolled_students
Finance    : budget_allocated, budget_consumed, budget_execution_rate, cost_per_student
RH         : teaching_headcount, admin_headcount, total_staff, absenteeism_rate, training_hours
ESG        : energy_consumption_kwh, carbon_footprint_ton, recycling_rate
Insertion  : employability_rate, national_convention_rate, international_convention_rate, insertion_delay_months
Recherche  : publications_count, active_projects, funding_tnd
Infra      : equipment_count, classroom_occupancy_rate

Règles STRICTES:
- N'invente pas de KPIs. Extrais seulement ce qui est explicitement chiffré dans le texte.
- Si le document est une liste de personnes/équipements sans agrégats, compte le TOTAL et retourne
  un seul KPI (ex: 15 lignes d'employés → teaching_headcount ou total_staff avec value=15).
- N'extrais JAMAIS un KPI par ligne individuelle (pas de emp1000, pas de "assistant admissions").
- indicator_key doit être l'un de ceux listés ci-dessus, rien d'autre.
- Si aucun KPI ne correspond, retourne [].

Format JSON pour chaque KPI:
{{"domain": "...", "indicator_key": "...", "value": 12.5, "unit": "%", "period_label": "2024-2025 S1", "confidence": 0.9}}

Retourne UNIQUEMENT le tableau JSON. Aucun texte autour.

Texte:
{text}
"""

VALIDATION_PROMPT = """Voici des KPIs extraits d'un document institutionnel:
{kpis}

Pour chaque KPI, évalue sa qualité et cohérence sur une échelle 0-100.
Retourne un objet JSON: {{"quality_score": 0-100, "issues": ["liste des problèmes détectés"], "valid_count": N}}
"""


def extract_kpis_from_text(text: str) -> list[dict]:
    """Send extracted text to Groq and get structured KPI data back."""
    if not text or len(text.strip()) < 30:
        return []

    # Truncate very long texts to avoid token limits
    truncated = text[:8000] if len(text) > 8000 else text

    try:
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "user", "content": EXTRACTION_PROMPT.format(text=truncated)}
            ],
            temperature=0.1,
            max_tokens=2048,
        )
        raw = completion.choices[0].message.content.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        data = json.loads(raw)
        if not isinstance(data, list):
            return []

        # Validate each item has required fields
        valid = []
        for item in data:
            if all(k in item for k in ("domain", "indicator_key", "value", "unit")):
                try:
                    item["value"] = float(item["value"])
                    item.setdefault("period_label", "N/A")
                    item.setdefault("confidence", 0.7)
                    valid.append(item)
                except (ValueError, TypeError):
                    continue
        return valid

    except (json.JSONDecodeError, Exception):
        return []


def validate_extracted_kpis(kpis: list[dict]) -> dict:
    """Ask Groq to evaluate the quality of extracted KPIs."""
    if not kpis:
        return {"quality_score": 0, "issues": ["Aucun KPI extrait"], "valid_count": 0}

    try:
        kpi_summary = json.dumps(kpis[:20], ensure_ascii=False, indent=2)
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "user", "content": VALIDATION_PROMPT.format(kpis=kpi_summary)}
            ],
            temperature=0.1,
            max_tokens=512,
        )
        raw = completion.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        result = json.loads(raw)
        result["valid_count"] = len(kpis)
        return result
    except Exception:
        return {"quality_score": 70, "issues": [], "valid_count": len(kpis)}
