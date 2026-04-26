from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from app.core.database import get_db
from app.core.limiter import limiter
from app.models.user import User
from app.dependencies.auth import get_current_user, get_scoped_institution_id
from app.services.kpi_service import get_latest_kpis
from app.ai.chatbot import build_context, query_chatbot, stream_chatbot

router = APIRouter(prefix="/chat", tags=["Chatbot IA"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    institution_id: Optional[int] = None
    stream: bool = False


@router.post("/")
@limiter.limit("30/minute")
def chat(
    request: Request,
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_id = get_scoped_institution_id(payload.institution_id, current_user)
    kpi_data = get_latest_kpis(db, scoped_id)

    from app.models.institution import Institution
    if scoped_id:
        inst = db.query(Institution).filter(Institution.id == scoped_id).first()
        inst_name = inst.name if inst else "Établissement"
    else:
        inst_name = "tous les établissements UCAR"

    context = build_context(kpi_data, inst_name)

    if payload.stream:
        def event_stream():
            for chunk in stream_chatbot(payload.question, context):
                # Encode newlines so they don't break the SSE line framing.
                # The frontend decodes \n back to real newlines before accumulating.
                encoded = chunk.replace("\\", "\\\\").replace("\n", "\\n")
                yield f"data: {encoded}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    answer = query_chatbot(payload.question, context)
    return {"question": payload.question, "answer": answer, "institution": inst_name}


@router.get("/suggestions")
def get_suggestions(current_user: User = Depends(get_current_user)):
    return {
        "suggestions": [
            "Quel est le taux d'abandon pour ce semestre ?",
            "Comparez les taux de réussite entre les établissements.",
            "Quel est l'état d'exécution du budget ?",
            "Y a-t-il des anomalies dans les données académiques ?",
            "Quelles sont les recommandations pour améliorer le taux d'employabilité ?",
            "Quel est le coût par étudiant cette année ?",
        ]
    }
