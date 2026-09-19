# SQLAlchemy models
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from pgvector.sqlalchemy import Vector


from sqlalchemy.dialects.postgresql import ARRAY

from app.database.connection import Base


class NewsItemModel(Base):
    """SQLAlchemy table definition, mirroring app/schemas/news.py's NewsItem."""

    __tablename__ = "news_items"
    __table_args__ = (
        UniqueConstraint("source", "source_id", name="uq_news_items_source_source_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Populated by scrapers / normalization
    source = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    author = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    scraped_at = Column(DateTime(timezone=True), nullable=False)

    # Populated later by LLM enrichment
    summary = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=False, default=list)



class NewsChunkModel(Base):
    """One chunk of an article's content, with its embedding vector."""

    __tablename__ = "news_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    news_item_id = Column(Integer, ForeignKey("news_items.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)

    __table_args__ = (
        Index(
            "ix_news_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_ip_ops"},
        ),
    )