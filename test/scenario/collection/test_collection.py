import tempfile
from pathlib import Path

from fino_filing.collection import Catalog, Collection, LocalStorage


class TestCollection:
    ########## instance check ##########
    def test_collection_init_with_no_config(self) -> None:
        collection = Collection()
        assert isinstance(collection, Collection)

    def test_collection_init(self) -> None:
        """Collection(storage, catalog)で初期化できる"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            storage = LocalStorage(base / "data")
            catalog = Catalog(str(base / "index.db"))
            collection = Collection(storage, catalog)

            assert collection._storage is storage
            assert collection._catalog is catalog
