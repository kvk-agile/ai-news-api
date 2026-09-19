# Ask endpoint: retrieve relevant chunks, then answer from that evidence only
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.answer_agent import answer_from_context
from app.agents.embedding_agent import create_embedding
from app.database.connection import get_db
from app.database.repository import get_news_item, search_similar_chunks
from app.schemas.news import AnswerCitation, AskRequest, AskResponse

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("/", response_model=AskResponse)
def ask_news(request: AskRequest, db: Session = Depends(get_db)):
    query_embedding = create_embedding(request.question)
    chunks = search_similar_chunks(db, query_embedding, limit=request.limit)

    if not chunks:
        return AskResponse(
            question=request.question,
            answer="Not enough information",
            supported=False,
            citations=[],
        )

    citations = []
    for chunk, _similarity in chunks:
        article = get_news_item(db, chunk.news_item_id)
        citations.append(
            AnswerCitation(
                news_item_id=article.id,
                source_id=article.source_id,
                title=article.title,
                url=article.url,
                chunk_content=chunk.content,
            )
        )

    grounded = answer_from_context(
        request.question,
        [citation.chunk_content for citation in citations],
    )

    return AskResponse(
        question=request.question,
        answer=grounded.answer,
        supported=grounded.supported,
        citations=citations,
    )