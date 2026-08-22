from pathlib import Path
import re

from app.scrapers.hackernews import scrape_top_stories

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"


def safe_filename(title: str) -> str:
    """Convert a title into a safe filename."""
    filename = re.sub(r"[^a-zA-Z0-9_-]+", "_", title)
    return filename.strip("_")[:80]


def run_ingestion() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    news_items = scrape_top_stories()

    for index, item in enumerate(news_items, start=1):
        filename = f"{index}_{safe_filename(item.title)}.json"
        filepath = OUTPUT_DIR / filename
        filepath.write_text(item.model_dump_json(indent=2), encoding="utf-8")

        print(f"Saved: {filepath}")


if __name__ == "__main__":
    run_ingestion()
