import hashlib
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pytest

from fino_filing import Catalog, Collection, Filing, LocalStorage


@pytest.fixture
def datetime_now() -> datetime:
    return datetime.now()


@pytest.fixture
def sample_filing() -> tuple[Filing, bytes]:
    """サンプル Filing と content の組。戻り値型: tuple[Filing, bytes]。"""
    content = b"test content"
    checksum = hashlib.sha256(content).hexdigest()
    filing = Filing(
        id="test_id_001",
        source="test_source",
        checksum=checksum,
        name="test_filing.txt",
        is_zip=False,
        format="xbrl",
        created_at=datetime.now(),
    )
    return filing, content


@pytest.fixture
def temp_work_dir() -> Iterator[Path]:
    """毎回新しい一時作業ディレクトリを作成する。テストごとに必ず別のディレクトリが渡される。"""
    with tempfile.TemporaryDirectory(prefix="collection_test_") as tmpdir:
        yield Path(tmpdir).resolve()


@pytest.fixture
def temp_storage() -> Iterator[LocalStorage]:
    """テスト用の一時ストレージを作成"""
    with tempfile.TemporaryDirectory(prefix="collection_test_") as tmpdir:
        storage = LocalStorage(Path(tmpdir) / "storage")
        yield storage


@pytest.fixture
def temp_catalog() -> Iterator[Catalog]:
    """テスト用の一時カタログを作成"""
    with tempfile.TemporaryDirectory(prefix="collection_test_") as tmpdir:
        catalog_path = Path(tmpdir) / "catalog.db"
        catalog = Catalog(str(catalog_path))
        yield catalog
        catalog.close()


@pytest.fixture
def temp_collection() -> Iterator[Collection]:
    """テスト用の一時 Collection（storage + catalog）"""
    with tempfile.TemporaryDirectory(prefix="collection_test_") as tmpdir:
        catalog_path = Path(tmpdir) / "index.db"
        catalog = Catalog(str(catalog_path))
        storage = LocalStorage(Path(tmpdir) / "storage")
        collection = Collection(storage=storage, catalog=catalog)
        yield collection
        catalog.close()
