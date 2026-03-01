"""Collector テスト用 fixtures"""

import hashlib
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pytest

from fino_filing import Catalog, Collection, EDGARFiling, LocalStorage
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edger import EdgerBulkData, EdgerConfig, EdgerSecApi


@pytest.fixture
def edger_config() -> EdgerConfig:
    return EdgerConfig(timeout=5)


@pytest.fixture
def sample_raw_document() -> RawDocument:
    """EDGAR 用のサンプル RawDocument（ネットワーク不要でパース・to_filing 検証用）"""
    content = b"<html><body>SEC filing index</body></html>"
    meta = {
        "cik": "0000320193",
        "accession_number": "0000320193-23-000106",
        "company_name": "Apple Inc.",
        "form_type": "10-K",
        "filing_date": datetime(2023, 10, 27),
        "period_of_report": datetime(2023, 9, 30),
        "sic_code": "3571",
        "state_of_incorporation": "CA",
        "fiscal_year_end": "09-30",
        "format": "htm",
        "primary_name": "0000320193-23-000106-index.htm",
        "_origin": "sec",
    }
    return RawDocument(content=content, meta=meta)


@pytest.fixture
def temp_collection() -> Iterator[tuple[Collection, Path]]:
    """テスト用の一時 Collection（storage + catalog）"""
    with tempfile.TemporaryDirectory(prefix="collector_test_") as tmpdir:
        base = Path(tmpdir)
        storage = LocalStorage(base / "storage")
        catalog_path = base / "index.db"
        catalog = Catalog(str(catalog_path))
        collection = Collection(storage=storage, catalog=catalog)
        yield collection, base
        catalog.close()
