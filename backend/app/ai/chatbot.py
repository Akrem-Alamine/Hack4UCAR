from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """Tu es un assistant intelligent spécialisé dans la gestion universitaire pour l'Université de Carthage (UCAR).
Tu analyses des données de performance (KPIs) des établissements universitaires affiliés et tu réponds en français.

Contexte des données disponibles:
{context}

Règles:
- Réponds toujours en français
- Sois précis et cite les chiffres quand ils sont disponibles
- Si tu n'as pas l'information, dis-le clairement
- Donne des recommandations pratiques basées sur les données
- Explique les anomalies ou tendances observées de manière simple
"""


def build_context(kpi_data: list[dict], institution_name: str = "tous les établissements") -> str:
    if not kpi_data:
        return "Aucune donnée KPI disponible pour le moment."

    lines = [f"Établissement(s): {institution_name}", ""]
    grouped: dict[str, list] = {}
    for record in kpi_data:
        domain = record.get("domain", "autre")
        grouped.setdefault(domain, []).append(record)

    domain_labels = {
        "academic": "Académique",
        "finance": "Finance",
        "hr": "Ressources Humaines",
        "esg": "ESG / RSE",
        "insertion": "Insertion Professionnelle",
        "research": "Recherche",
        "infrastructure": "Infrastructure",
        "partnerships": "Partenariats",
        "student_life": "Vie Estudiantine",
    }

    for domain, records in grouped.items():
        label = domain_labels.get(domain, domain.capitalize())
        lines.append(f"[{label}]")
        for r in records[:10]:
            lines.append(
                f"  - {r.get('indicator_key', '')}: {r.get('value', '')} {r.get('unit', '')} "
                f"({r.get('period_label', '')})"
            )
        lines.append("")

    return "\n".join(lines)


def query_chatbot(question: str, context: str) -> str:
    system_content = SYSTEM_PROMPT.format(context=context)

    completion = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": question},
        ],
        temperature=0.7,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
    )
    return completion.choices[0].message.content


def stream_chatbot(question: str, context: str):
    system_content = SYSTEM_PROMPT.format(context=context)

    completion = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": question},
        ],
        temperature=0.7,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
    )
    for chunk in completion:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def generate_report_narrative(kpi_summary: dict, period: str, institution_name: str) -> str:
    prompt = f"""Génère un résumé exécutif en français pour le rapport institutionnel suivant.

Établissement: {institution_name}
Période: {period}
Données KPIs:
{kpi_summary}

Le résumé doit:
- Être structuré en 3-4 paragraphes
- Mettre en avant les points forts et les points d'amélioration
- Mentionner les anomalies ou alertes si présentes
- Donner 2-3 recommandations concrètes
- Rester factuel et professionnel
"""
    completion = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_completion_tokens=2048,
        stream=False,
    )
    return completion.choices[0].message.content
