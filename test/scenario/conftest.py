"""Scenario-only fixtures (collector response fixtures come from root test/conftest plugins)."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Iterator

import pytest

from fino_filing import Catalog, Collection, LocalStorage


@pytest.fixture
def temp_collection_pair() -> Iterator[tuple[Collection, Path]]:
    """Temporary Collection with storage root path (for collector scenarios)."""
    with tempfile.TemporaryDirectory(prefix="scenario_collector_") as tmpdir:
        base = Path(tmpdir)
        storage = LocalStorage(base / "storage")
        catalog_path = base / "index.db"
        catalog = Catalog(str(catalog_path))
        collection = Collection(storage=storage, catalog=catalog)
        yield collection, base
        catalog.close()
