"""Collector テスト用 fixtures"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pytest

from fino_filing import Catalog, Collection, LocalStorage
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edger import EdgerConfig
from fino_filing.collector.edinet import EdinetConfig


@pytest.fixture
def edinet_config() -> EdinetConfig:
    return EdinetConfig(api_key="test-api-key", timeout=5)


@pytest.fixture
def sample_edinet_raw_document() -> RawDocument:
    """EDINET 用のサンプル RawDocument（ネットワーク不要でパース・build_filing 検証用）"""
    content = b"%PDF-1.4 dummy edinet document"
    meta = {
        "doc_id": "S100ABCD1234567890",
        "edinet_code": "E12345",
        "sec_code": "12345",
        "jcn": "1234567890123",
        "filer_name": "株式会社テスト",
        "ordinance_code": "010",
        "form_code": "030000",
        "doc_type_code": "120",
        "doc_description": "有価証券報告書",
        "period_start": datetime(2023, 4, 1),
        "period_end": datetime(2024, 3, 31),
        "submit_datetime": datetime(2024, 6, 28, 10, 0, 0),
        "parent_doc_id": None,
    }
    return RawDocument(content=content, meta=meta)


@pytest.fixture
def edger_config() -> EdgerConfig:
    return EdgerConfig(user_agent_email="test@example.com", timeout=5)


@pytest.fixture
def sample_raw_document() -> RawDocument:
    """EDGAR 用のサンプル RawDocument（ネットワーク不要でパース・build_filing 検証用）"""
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
        "_origin": "documents",
    }
    return RawDocument(content=content, meta=meta)


@pytest.fixture
def temp_collection() -> Iterator[tuple[Collection, Path]]:
    """テスト用の一時 Collection（storage + catalog）。collector 用は (collection, base_path) を返す。"""
    with tempfile.TemporaryDirectory(prefix="collector_test_") as tmpdir:
        base = Path(tmpdir)
        storage = LocalStorage(base / "storage")
        catalog_path = base / "index.db"
        catalog = Catalog(str(catalog_path))
        collection = Collection(storage=storage, catalog=catalog)
        yield collection, base
        catalog.close()
