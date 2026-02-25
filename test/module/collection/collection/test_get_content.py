from fino_filing import Catalog, Collection, Filing
from fino_filing.collection.storages import LocalStorage


class TestCollection_GetContent:
    """
    Collection.get_content(). 観点: 正常系と異常系（not_found）
    """

    # TODO: 既存のdbが存在する場合に既存のバイト列が返る

    def test_get_content_returns_saved_bytes(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        sample_filing: tuple[Filing, bytes],
    ) -> None:
        """正常系: add 後に get_content で同じバイト列が取得できる"""
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        filing, content = sample_filing
        collection.add(filing, content)

        retrieved = collection.get_content(filing.id)

        assert retrieved is not None
        assert retrieved == content

    def test_get_content_returns_none_when_not_found(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
    ) -> None:
        """仕様: 存在しない id のとき None を返す。検証: 戻り値が None"""
        collection = Collection(storage=temp_storage, catalog=temp_catalog)

        result = collection.get_content("nonexistent_id")

        assert result is None
