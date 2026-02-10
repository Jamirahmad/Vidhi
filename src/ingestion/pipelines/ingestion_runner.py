"""
Ingestion Runner

System entry-point for document ingestion.
Responsible for:
- wiring fetchers to the ingestion pipeline
- executing batch ingestion jobs
- handling failures and observability

This module is intentionally thin.
"""

from __future__ import annotations

import sys
from typing import Dict, Iterable, List, Optional

from src.utils.logging_utils import get_logger

# Fetchers
from src.ingestion.fetchers.hc_scraper import HighCourtScraper
from src.ingestion.fetchers.sc_scraper import SupremeCourtScraper
from src.ingestion.fetchers.tribunal_scraper import TribunalScraper
from src.ingestion.fetchers.indian_kanoon_connector import IndianKanoonConnector
from src.ingestion.fetchers.upload_handler import UploadHandler

# Pipeline
from src.ingestion.pipelines.ingestion_pipeline import (
    IngestionPipeline,
    IngestionPipelineError,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Fetcher Registry
# ---------------------------------------------------------------------

FETCHER_REGISTRY = {
    "high_court": HighCourtScraper,
    "supreme_court": SupremeCourtScraper,
    "tribunal": TribunalScraper,
    "indian_kanoon": IndianKanoonConnector,
    "upload": UploadHandler,
}


# ---------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------

class IngestionRunner:
    """
    Coordinates fetchers and ingestion pipeline.
    """

    def __init__(self) -> None:
        self.pipeline = IngestionPipeline()

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def run(
        self,
        *,
        source: str,
        fetcher_kwargs: Optional[Dict[str, object]] = None,
    ) -> List[Dict[str, object]]:
        """
        Run ingestion for a given source.

        Args:
            source: source key registered in FETCHER_REGISTRY
            fetcher_kwargs: parameters passed to the fetcher

        Returns:
            List of chunked documents
        """
        fetcher_kwargs = fetcher_kwargs or {}

        logger.info("Starting ingestion | source=%s", source)

        fetcher = self._initialize_fetcher(
            source=source,
            fetcher_kwargs=fetcher_kwargs,
        )

        raw_records = self._fetch_records(fetcher)

        chunks = self._ingest_records(raw_records)

        logger.info(
            "Ingestion finished | source=%s | chunks=%s",
            source,
            len(chunks),
        )

        return chunks

    # -----------------------------------------------------------------
    # Internals
    # -----------------------------------------------------------------

    def _initialize_fetcher(
        self,
        *,
        source: str,
        fetcher_kwargs: Dict[str, object],
    ):
        if source not in FETCHER_REGISTRY:
            raise ValueError(
                f"Unknown ingestion source '{source}'. "
                f"Valid sources: {list(FETCHER_REGISTRY.keys())}"
            )

        fetcher_cls = FETCHER_REGISTRY[source]
        return fetcher_cls(**fetcher_kwargs)

    def _fetch_records(self, fetcher) -> Iterable[Dict[str, object]]:
        try:
            records = fetcher.fetch()
        except Exception as exc:
            logger.exception("Fetcher failed")
            raise RuntimeError("Fetcher execution failed") from exc

        if not records:
            logger.warning("No records fetched")
            return []

        logger.info("Fetched %s raw records", len(records))
        return records

    def _ingest_records(
        self,
        records: Iterable[Dict[str, object]],
    ) -> List[Dict[str, object]]:
        try:
            return self.pipeline.ingest_records(records=records)
        except IngestionPipelineError:
            raise
        except Exception as exc:
            logger.exception("Pipeline execution failed")
            raise RuntimeError("Ingestion pipeline failed") from exc


# ---------------------------------------------------------------------
# Optional CLI Execution
# ---------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> None:
    """
    CLI entry-point.
    Example:
        python -m src.ingestion.pipelines.ingestion_runner high_court
    """
    argv = argv or sys.argv[1:]

    if not argv:
        raise SystemExit("Usage: ingestion_runner.py <source>")

    source = argv[0]

    runner = IngestionRunner()
    runner.run(source=source)


if __name__ == "__main__":
    main()
