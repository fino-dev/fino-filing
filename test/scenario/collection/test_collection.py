import tempfile
from pathlib import Path

from fino_filing.collection import Collection, FlatLocalStorage, IndexDB


class TestCollection:
    ########## instance check ##########
    def test_collection_init_with_no_config(self) -> None:
        collection = Collection()
        assert isinstance(collection, Collection)

    def test_collection_init(self) -> None:
        """Collection(storage, index_db)で初期化できる"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            storage = FlatLocalStorage(base / "data")
            index_db = IndexDB(str(base / "index.db"))
            collection = Collection(storage, index_db)

            assert collection.storage is storage
            assert collection.index_db is index_db
