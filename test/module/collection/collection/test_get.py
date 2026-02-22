from datetime import datetime

import hashlib

from fino_filing import Catalog, Collection, EDINETFiling, Filing, LocalStorage


class TestCollection_Get:
    """
    Collectionのget()メソッドをテストする。
    - 正常系: add後にgetでFilingとcontentが取得できる
    - 正常系: EDINETFilingで保存した場合はgetでEDINETFilingとして返る
    - 正常系: findでも保存時の具象クラスで返る
    - 正常型: 存在しないidでNoneが返る
    """

    def test_get_filing_and_content_success(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        sample_filing: tuple[Filing, bytes],
    ) -> None:
        """Filingとcontentが取得できる"""
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        filing, content = sample_filing

        # add
        saved_filing, actual_path = collection.add(filing, content)

        assert actual_path is not None
        assert isinstance(actual_path, str)
        assert isinstance(saved_filing, Filing)

        assert temp_storage.exists(filing.id)
        assert temp_storage.exists(saved_filing.id)

        # catalogに登録されていることを確認
        filing, content = collection.get(filing.id)
        assert filing is not None
        assert isinstance(filing, Filing)
        assert filing.id == saved_filing.id
        assert filing.name == saved_filing.name
        assert content is not None
        assert isinstance(content, bytes)
        assert content == b"test content"

    def test_get_filing_returns_edinet_filing_when_saved_as_edinet(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        datetime_now: datetime,
    ) -> None:
        """EDINETFilingでaddした場合、get_filingでEDINETFilingとして復元される"""
        content = b"test content"
        checksum = hashlib.sha256(content).hexdigest()
        edinet_filing = EDINETFiling(
            id="test_id_edinet",
            checksum=checksum,
            name="test_filing.txt",
            is_zip=False,
            created_at=datetime_now,
            edinet_code="test_edinet_code",
            sec_code="test_sec_code",
            jcn="test_jcn",
            filer_name="test_filer_name",
            ordinance_code="test_ordinance_code",
            form_code="test_form_code",
            doc_type_code="test_doc_type_code",
            doc_description="test_doc_description",
            period_start=datetime_now,
            period_end=datetime_now,
            submit_datetime=datetime_now,
        )
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        collection.add(edinet_filing, content)

        filing = collection.get_filing(edinet_filing.id)
        assert filing is not None
        assert isinstance(filing, EDINETFiling)
        assert filing.id == edinet_filing.id
        assert filing.edinet_code == edinet_filing.edinet_code
        assert filing.filer_name == edinet_filing.filer_name

    def test_find_returns_edinet_filing_when_saved_as_edinet(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        datetime_now: datetime,
    ) -> None:
        """EDINETFilingでaddした場合、findでEDINETFilingとして復元される"""
        content = b"test content"
        checksum = hashlib.sha256(content).hexdigest()
        edinet_filing = EDINETFiling(
            id="test_id_edinet_find",
            checksum=checksum,
            name="test_filing.txt",
            is_zip=False,
            created_at=datetime_now,
            edinet_code="test_edinet_code",
            sec_code="test_sec_code",
            jcn="test_jcn",
            filer_name="test_filer_name",
            ordinance_code="test_ordinance_code",
            form_code="test_form_code",
            doc_type_code="test_doc_type_code",
            doc_description="test_doc_description",
            period_start=datetime_now,
            period_end=datetime_now,
            submit_datetime=datetime_now,
        )
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        collection.add(edinet_filing, content)

        results = collection.find(limit=10)
        assert len(results) >= 1
        filing = next(f for f in results if f.id == edinet_filing.id)
        assert isinstance(filing, EDINETFiling)
        assert filing.edinet_code == edinet_filing.edinet_code
        assert filing.filer_name == edinet_filing.filer_name

    def test_get_filing_and_content_not_found(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        sample_filing: tuple[Filing, bytes],
    ) -> None:
        """存在しない場合、Noneが返る"""
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        filing, content = sample_filing
        collection.add(filing, content)

        filing, content = collection.get("nonexistent_id")
        assert filing is None
        assert content is None


#     def test_add_filing_with_checksum_mismatch(
#         self, temp_storage, temp_catalog, sample_filing
#     ) -> None:
#         """checksumが一致しない場合のエラーテスト"""
#         collection = Collection(storage=temp_storage, catalog=temp_catalog)
#         filing, _ = sample_filing

#         # 異なるcontentでchecksum不一致を引き起こす
#         wrong_content = b"different content"

#         with pytest.raises(ValueError) as exc_info:
#             collection.add(filing, wrong_content)

#         assert "Checksum mismatch" in str(exc_info.value)

#     def test_add_filing_with_missing_id(self, temp_storage, temp_catalog) -> None:
#         """idがNoneの場合のエラーテスト"""
#         collection = Collection(storage=temp_storage, catalog=temp_catalog)

#         content = b"test content"
#         checksum = hashlib.sha256(content).hexdigest()

#         # idをNoneで作成（動的フィールドとして設定）
#         filing = Filing(
#             id="temp_id",
#             source="test_source",
#             checksum=checksum,
#             name="test.txt",
#             is_zip=False,
#             created_at=datetime.now(),
#         )
#         # idを動的に削除
#         filing._fields.pop("id")

#         with pytest.raises(ValueError) as exc_info:
#             collection.add(filing, content)

#         assert "id is required" in str(exc_info.value)

#     def test_add_filing_with_duplicate_id(
#         self, temp_storage, temp_catalog, sample_filing
#     ) -> None:
#         """既に同じidが存在する場合のエラーテスト"""
#         collection = Collection(storage=temp_storage, catalog=temp_catalog)
#         filing, content = sample_filing

#         # 最初の追加は成功
#         collection.add(filing, content)

#         # 同じidで再度追加しようとするとエラー
#         with pytest.raises(ValueError) as exc_info:
#             collection.add(filing, content)

#         assert "already exists" in str(exc_info.value)
