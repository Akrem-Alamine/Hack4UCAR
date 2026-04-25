"""
Track 1 — AI-powered KPI extraction from unstructured text.
Uses Groq to identify and structure KPI data from OCR/PDF text.
"""
import json
import re
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

EXTRACTION_PROMPT = """Tu es un expert en analyse de données universitaires. Analyse le texte suivant extrait d'un document institutionnel et extrais tous les indicateurs de performance (KPIs) que tu peux identifier.

Pour chaque KPI trouvé, retourne un objet JSON avec ces champs exacts:
- domain: l'un des domaines suivants: academic, finance, hr, esg, insertion, research, infrastructure, partnerships, student_life
- indicator_key: identifiant snake_case du KPI (ex: success_rate, dropout_rate, budget_execution_rate)
- value: valeur numérique (nombre uniquement)
- unit: unité (%, TND, nombre, kWh, mois, etc.)
- period_label: période concernée si mentionnée (ex: "2024-2025 S1"), sinon "N/A"
- confidence: score de confiance 0-1 sur l'extraction

Retourne UNIQUEMENT un tableau JSON valide. Aucun texte avant ou après.
Si aucun KPI n'est identifiable, retourne [].

Texte du document:
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
