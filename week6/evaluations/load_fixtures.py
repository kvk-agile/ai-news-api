import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from app.agents.embedding_agent import create_embedding
from app.database.connection import SessionLocal
from app.database.models import NewsChunkModel, NewsItemModel
from app.database.repository import insert_news_chunks, insert_news_item
from app.schemas.news import NewsItem
from app.services.indexing import chunk_text

FIXTURE_SOURCE = "eval-fixture"
FIXTURES_PATH = Path(__file__).parent / "fixtures.json"


def load_fixtures() -> None:
    """Insert the fixture articles and index their chunks. Safe to re-run."""

    fixtures = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))
    db = SessionLocal()
    try:
        for fixture in fixtures:
            item = NewsItem(**fixture, scraped_at=datetime.now(timezone.utc))
            row = insert_news_item(db, item)

            if row is None:
                print(f"Already present: {fixture['title']}")
                continue

            chunks = [
                {
                    "chunk_index": index,
                    "content": piece,
                    "embedding": create_embedding(piece),
                }
                for index, piece in enumerate(chunk_text(fixture["content"]))
            ]
            insert_news_chunks(db, row.id, chunks)
            print(f"Inserted: {fixture['title']} ({len(chunks)} chunk)")
    finally:
        db.close()


def cleanup_fixtures() -> None:
    """Delete fixture chunks first, then the fixture articles."""

    db = SessionLocal()
    try:
        fixture_ids = [
            row.id
            for row in db.query(NewsItemModel.id).filter(
                NewsItemModel.source == FIXTURE_SOURCE
            )
        ]
        chunks_deleted = (
            db.query(NewsChunkModel)
            .filter(NewsChunkModel.news_item_id.in_(fixture_ids))
            .delete(synchronize_session=False)
        )
        items_deleted = (
            db.query(NewsItemModel)
            .filter(NewsItemModel.source == FIXTURE_SOURCE)
            .delete(synchronize_session=False)
        )
        db.commit()
        print(f"Deleted {chunks_deleted} chunks and {items_deleted} fixture articles.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load or remove evaluation fixtures.")
    parser.add_argument(
        "--cleanup", action="store_true", help="Remove the fixture articles."
    )
    args = parser.parse_args()

    if args.cleanup:
        cleanup_fixtures()
    else:
        load_fixtures()