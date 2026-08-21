from pathlib import Path

from app.agents.news_agent import enrich_article
from app.schemas.news import NewsItem

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "enriched"


def run_enrichment() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for filepath in sorted(INPUT_DIR.glob("*.json")):
        item = NewsItem.model_validate_json(filepath.read_text(encoding="utf-8"))

        if not item.content:
            continue

        enrichment = enrich_article(item.title, item.content)

        enriched_item = item.model_copy(
            update={"summary": enrichment.summary, "tags": enrichment.tags}
        )

        out_path = OUTPUT_DIR / filepath.name
        out_path.write_text(enriched_item.model_dump_json(indent=2), encoding="utf-8")

        print(f"Enriched: {out_path}")


if __name__ == "__main__":
    run_enrichment()
