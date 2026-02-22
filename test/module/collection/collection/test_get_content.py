from fino_filing import Catalog, Collection, Filing, LocalStorage


class TestCollection_GetContent:
    """
    Collectionのget_content()をテストする。
    - 正常系: add後にget_contentで同じバイト列が取得できる
    - 正常系: 存在しないidでNoneが返る
    """

    # TODO: 既存のdbが存在する場合に既存のバイト列が返る

    def test_get_content_returns_saved_bytes(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        sample_filing: tuple[Filing, bytes],
    ) -> None:
        """保存したファイル本体をIDで取得できる"""
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
        """存在しないIDの場合はNone"""
        collection = Collection(storage=temp_storage, catalog=temp_catalog)

        result = collection.get_content("nonexistent_id")

        assert result is None
