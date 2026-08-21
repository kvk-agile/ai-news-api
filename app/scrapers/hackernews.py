from datetime import datetime, timezone
from pathlib import Path
import re
import requests
import trafilatura

from app.schemas.news import NewsItem

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

# Create local output folder at the project root, regardless of cwd
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename(title: str) -> str:
    """Convert a title into a safe filename."""
    filename = re.sub(r"[^a-zA-Z0-9_-]+", "_", title)
    return filename.strip("_")[:80]


# Get top Hacker News story IDs
story_ids = requests.get(TOP_STORIES_URL, timeout=10).json()

saved = 0

for story_id in story_ids:
    if saved >= 5:
        break

    story = requests.get(
        ITEM_URL.format(story_id),
        timeout=10
    ).json()

    url = story.get("url")
    title = story.get("title")

    # Some HN posts don't link to an external webpage
    if not url or not title:
        continue

    # Download webpage
    downloaded = trafilatura.fetch_url(url)

    if not downloaded:
        continue

    # Extract main article text
    content = trafilatura.extract(downloaded)

    if not content:
        continue

    # Normalize into the canonical NewsItem shape
    news_item = NewsItem(
        source="hackernews",
        source_id=str(story_id),
        title=title,
        url=url,
        author=story.get("by"),
        content=content,
        scraped_at=datetime.now(timezone.utc),
    )

    filename = f"{saved + 1}_{safe_filename(title)}.json"
    filepath = OUTPUT_DIR / filename
    filepath.write_text(news_item.model_dump_json(indent=2), encoding="utf-8")

    print(f"Saved: {filepath}")
    saved += 1
