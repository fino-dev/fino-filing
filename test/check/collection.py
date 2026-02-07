"""Collection初期化・基本操作チェック"""

import tempfile
from datetime import datetime
from pathlib import Path

from fino_filing.collection import Collection, Filing, FlatLocalStorage
from fino_filing.collection.catalog import Catalog


def test_collection_init() -> None:
    """Collection(storage, catalog)で初期化できる"""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        storage = FlatLocalStorage(base / "data")
        catalog = Catalog(str(base / "index.db"))
        collection = Collection(storage, catalog)

        assert collection._storage is storage
        assert collection._catalog is catalog


def test_collection_add_get() -> None:
    """add/getでFilingを保存・取得できる"""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        storage = FlatLocalStorage(base / "data")
        catalog = Catalog(str(base / "index.db"))
        collection = Collection(storage, catalog)

        content = b"test content"
        import hashlib

        checksum = hashlib.sha256(content).hexdigest()
        filing = Filing(
            id="test:001:abc12345",
            source="test",
            checksum=checksum,
            name="test.zip",
            is_zip=True,
            created_at=datetime(2024, 1, 15),
        )

        path = collection.add(filing, content)
        assert path

        got = collection.get("test:001:abc12345")
        assert got is not None
        assert got.get("id") == filing.get("id")
        assert got.get_content() == content
