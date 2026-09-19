import tiktoken

from app.agents.embedding_agent import create_embedding
from app.database.connection import SessionLocal
from app.database.repository import get_unindexed_news_items, insert_news_chunks

encoding = tiktoken.get_encoding("cl100k_base")


def chunk_text(text: str, max_tokens: int = 500) -> list[str]:
    """Split text into chunks of roughly max_tokens tokens each."""
    tokens = encoding.encode(text)
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i : i + max_tokens]
        chunks.append(encoding.decode(chunk_tokens))

    return chunks


def run_indexing() -> None:
    db = SessionLocal()
    try:
        for row in get_unindexed_news_items(db):
            if not row.content:
                continue

            pieces = chunk_text(row.content)

            chunks = []
            for i, piece in enumerate(pieces):
                embedding = create_embedding(piece)
                chunks.append({
                    "chunk_index": i,
                    "content": piece,
                    "embedding": embedding,
                })

            insert_news_chunks(db, row.id, chunks)

            print(f"Indexed: {row.title} ({len(chunks)} chunks)")
    finally:
        db.close()


if __name__ == "__main__":
    run_indexing()