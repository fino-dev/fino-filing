from fino_filing import Catalog, Collection, Filing, LocalStorage


class TestCollection_GetFiling:
    """
    Collectionのget_filing()メソッドをテストする。
    - 正常系: add後にget_filingでFilingが取得できる（fieldsとdataが一致した状態で取得できる）
    - 正常系: add後にget_filingで継承したFilingが取得できる（追加したfieldsとdefaultsとdataが一致した状態で取得できる）
    - 正常系: 存在しないidでNoneが返る
    """

    # TODO: 既存のdbが存在する場合に既存のFilingが返る

    def test_get_filing_success(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        sample_filing: tuple[Filing, bytes],
    ) -> None:
        """Filingが取得できる"""
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        filing, content = sample_filing
        collection.add(filing, content)

        retrieved = collection.get_filing(filing.id)

        assert retrieved is not None
        assert retrieved == filing

    def test_get_filing_not_found(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
    ) -> None:
        """存在しない場合、Noneが返る"""
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        filing = collection.get_filing("nonexistent_id")

        assert filing is None
