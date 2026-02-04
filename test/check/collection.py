"""Collection初期化・基本操作チェック"""

import tempfile
from datetime import datetime
from pathlib import Path

from fino_filing.collection import Collection, FlatLocalStorage, IndexDB
from fino_filing.collection.models import Filing


def test_collection_init() -> None:
    """Collection(storage, index_db)で初期化できる"""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        storage = FlatLocalStorage(base / "data")
        index_db = IndexDB(str(base / "index.db"))
        collection = Collection(storage, index_db)

        assert collection.storage is storage
        assert collection.index_db is index_db


def test_collection_add_get() -> None:
    """add/getでFilingを保存・取得できる"""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        storage = FlatLocalStorage(base / "data")
        index_db = IndexDB(str(base / "index.db"))
        collection = Collection(storage, index_db)

        content = b"test content"
        import hashlib

        checksum = hashlib.sha256(content).hexdigest()
        filing = Filing(
            filing_id="test:001:abc12345",
            source="test",
            checksum=checksum,
            submit_date=datetime(2024, 1, 15),
            document_type="120",
        )

        path = collection.add(filing, content)
        assert path
        assert collection.exists("test:001:abc12345")

        got = collection.get("test:001:abc12345")
        assert got is not None
        assert got.filing_id == filing.filing_id
        assert got.get_content() == content
