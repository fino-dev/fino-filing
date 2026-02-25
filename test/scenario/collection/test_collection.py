"""シナリオ: Collection の初期化（module の test_init と重複するがシナリオとして配置）"""

import tempfile
from pathlib import Path

from fino_filing import Catalog, Collection, LocalStorage


class TestCollection_Scenario_Init:
    """Collection 初期化のシナリオ。観点: 正常系"""

    def test_collection_init_with_storage_and_catalog(self) -> None:
        """Collection(storage, catalog) で初期化できる"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            storage = LocalStorage(base / "data")
            catalog = Catalog(str(base / "index.db"))
            collection = Collection(storage=storage, catalog=catalog)
            assert collection._storage is storage
            assert collection._catalog is catalog
            catalog.close()
