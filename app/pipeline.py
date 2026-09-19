from app.services.ingestion import run_ingestion
from app.services.enrichment import run_enrichment
from app.services.indexing import run_indexing


def run_pipeline() -> None:
    print("Starting ingestion...")
    run_ingestion()

    print("Starting enrichment...")
    run_enrichment()

    print("Starting indexing...")
    run_indexing()

    print("Pipeline complete.")


if __name__ == "__main__":
    run_pipeline()