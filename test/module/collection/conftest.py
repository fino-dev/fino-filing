import hashlib
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pytest

from fino_filing import Catalog, Filing, LocalStorage


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
def sample_filing():
    """サンプルFilingを作成（id / created_at は内部生成）"""
    content = b"test content"
    checksum = hashlib.sha256(content).hexdigest()

    filing = Filing(
        source="test_source",
        checksum=checksum,
        name="test_filing.txt",
        is_zip=False,
        format="xbrl",
    )

    return filing, content
