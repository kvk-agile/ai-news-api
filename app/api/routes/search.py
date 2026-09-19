# Search endpoints
import os

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.agents.embedding_agent import create_embedding
from app.database.connection import get_db
from app.database.repository import get_news_item, search_similar_chunks
from app.schemas.news import SearchResult

router = APIRouter(prefix="/search", tags=["search"])


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("SEARCH_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.get("/", response_model=list[SearchResult])
def search(q: str, db: Session = Depends(get_db), _: None = Depends(verify_api_key)):
    query_embedding = create_embedding(q)
    chunks = search_similar_chunks(db, query_embedding)

    results = []
    for chunk, similarity in chunks:
        article = get_news_item(db, chunk.news_item_id)
        results.append(
            SearchResult(
                news_item_id=article.id,
                title=article.title,
                url=article.url,
                chunk_content=chunk.content,
                similarity=similarity,
            )
        )

    return results