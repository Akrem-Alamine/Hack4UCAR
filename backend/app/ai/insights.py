"""
Track 2 & 3 — AI-powered domain insights.
Generates plain-language analysis of KPI data for non-technical users.
"""
import json
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

INSIGHTS_PROMPT = """Tu es un expert en analyse institutionnelle universitaire. Analyse les KPIs suivants pour l'établissement "{institution}" dans le domaine "{domain_label}" et génère des insights en français.

Données KPIs:
{kpi_data}

Génère une analyse structurée avec exactement ces 3 sections:
1. **Points forts** (2-3 éléments positifs basés sur les données)
2. **Points d'attention** (2-3 éléments préoccupants ou anomalies)
3. **Recommandations** (2-3 actions concrètes et réalistes)

Sois factuel, cite les chiffres, et reste en français. Sois concis (max 200 mots au total).
"""

ANOMALY_EXPLAIN_PROMPT = """Un KPI universitaire présente une anomalie statistique (score Z: {z_score}).

KPI: {indicator_label}
Valeur actuelle: {value} {unit}
Établissement: {institution}
Période: {period}

Explique en 2-3 phrases simples:
1. Ce que signifie cette anomalie
2. Les causes probables dans un contexte universitaire tunisien
3. L'action recommandée immédiate

Réponds en français, sans jargon statistique.
"""


def generate_domain_insights(
    kpi_data: list[dict],
    domain: str,
    institution_name: str,
    domain_label: str,
) -> dict:
    if not kpi_data:
        return {
            "domain": domain,
            "institution": institution_name,
            "insights": "Aucune donnée disponible pour ce domaine.",
            "strengths": [],
            "concerns": [],
            "recommendations": [],
        }

    kpi_lines = "\n".join(
        f"- {item.get('indicator_key', '')}: {item.get('value', '')} {item.get('unit', '')} ({item.get('period_label', '')})"
        for item in kpi_data[:15]
    )

    try:
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{
                "role": "user",
                "content": INSIGHTS_PROMPT.format(
                    institution=institution_name,
                    domain_label=domain_label,
                    kpi_data=kpi_lines,
                )
            }],
            temperature=0.6,
            max_tokens=600,
        )
        text = completion.choices[0].message.content.strip()
    except Exception as e:
        text = f"Analyse temporairement indisponible : {e}"

    return {
        "domain": domain,
        "institution": institution_name,
        "insights": text,
    }


def explain_anomaly(
    indicator_key: str,
    value: float,
    unit: str,
    z_score: float,
    institution_name: str,
    period_label: str,
) -> str:
    from app.lib.labels import INDICATOR_LABELS
    indicator_label = INDICATOR_LABELS.get(indicator_key, indicator_key.replace("_", " ").title())

    try:
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{
                "role": "user",
                "content": ANOMALY_EXPLAIN_PROMPT.format(
                    z_score=round(z_score, 2),
                    indicator_label=indicator_label,
                    value=value,
                    unit=unit,
                    institution=institution_name,
                    period=period_label,
                )
            }],
            temperature=0.5,
            max_tokens=300,
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        direction = "élevée" if z_score > 0 else "faible"
        return (
            f"La valeur {value} {unit} est statistiquement {direction} par rapport à l'historique "
            f"(score Z: {round(z_score, 2)}). Une vérification des données source est recommandée."
        )
