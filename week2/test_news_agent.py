#uv run python -m week2.test_news_agent
import json
from pathlib import Path
from app.agents.news_agent import enrich_article
data = json.loads(Path("data/raw/1_Kobo_can_run_apps_now.json").read_text())

result = enrich_article(data["title"], data["content"])
#print(result)
print(result.model_dump_json(indent=2))