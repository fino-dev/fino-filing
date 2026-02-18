from fino_filing import Catalog, Collection, Filing, LocalStorage


class TestCollection_Add:
    """
    Collectionのadd()メソッドをテストする。
    - 正常系: 正しいchecksum、有効なFilingで追加成功
    - 異常系: checksumが一致しない場合
    - 異常系: idがNoneの場合
    - 異常系: 既に同じidが存在する場合
    """

    def test_add_filing_success(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        sample_filing: tuple[Filing, bytes],
    ) -> None:
        """正常なFiling追加のテスト"""
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        filing, content = sample_filing

        # Filing追加
        saved_filing, actual_path = collection.add(filing, content)

        assert actual_path is not None
        assert isinstance(actual_path, str)
        assert isinstance(saved_filing, Filing)

        assert temp_storage.exists(filing.id)
        assert temp_storage.exists(saved_filing.id)

        # catalogに登録されていることを確認
        retrieved = collection.get(filing.id)
        assert retrieved is not None
        assert retrieved.id == filing.id
        assert retrieved.name == filing.name

        assert retrieved.id == saved_filing.id
        assert retrieved.name == saved_filing.name


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
