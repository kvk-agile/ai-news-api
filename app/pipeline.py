# Batch ingestion/enrichment entry point
def run_pipeline():
    return [
        {
            "source": "openai",
            "title": "Example AI news",
            "summary": "This is mock data for Week 1."
        }
    ]