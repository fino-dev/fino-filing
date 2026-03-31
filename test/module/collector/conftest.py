"""Collector テスト用 fixtures"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pytest

from fino_filing import Catalog, Collection, LocalStorage
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edger import EdgerConfig


@pytest.fixture
def edger_config() -> EdgerConfig:
    return EdgerConfig(user_agent_email="test@example.com", timeout=5)


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
