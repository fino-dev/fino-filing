"""Collectionのテスト"""

import os
from pathlib import Path

from fino_filing.collection.catalog import Catalog
from fino_filing.collection.collection import Collection
from fino_filing.collection.storages import LocalStorage


class TestCollection_Initialize:
    """
    Collectionの初期化をテストする。
    - 正常系: デフォルト初期化（storage, catalogなし）
    - 正常系: カスタム初期化（storage, catalog指定）
    """

    # TODO: 既存のdbが存在する場合をチェック

    def test_collection_init_with_defaults(self, temp_work_dir: Path) -> None:
        """デフォルト初期化（storage, catalogなし）のテスト。CWDにstorageとcatalogが作成される。"""
        default_collection_dir = temp_work_dir / ".fino" / "collection"

        # 初期化前にディレクトリが存在しないことを確認（この実行で作成されることを検証するため）
        assert not default_collection_dir.exists(), (
            "default_dir must not exist before Collection()"
        )

        old_cwd = os.getcwd()
        os.chdir(temp_work_dir)

        try:
            collection = Collection()

            # この実行でデフォルトのディレクトリが作成されていることを確認
            assert collection._storage.base_dir == default_collection_dir
            assert default_collection_dir.exists()
            assert default_collection_dir.is_dir()
        finally:
            os.chdir(old_cwd)

    def test_collection_init_with_custom_components(
        self, temp_storage: LocalStorage, temp_catalog: Catalog, temp_work_dir: Path
    ) -> None:
        """カスタムコンポーネントを指定した初期化のテスト。CWDにstorageとcatalogが作成される。"""
        default_collection_dir = temp_work_dir / ".fino" / "collection"

        # 初期化前にディレクトリが存在しないことを確認（この実行で作成されることを検証するため）
        assert not default_collection_dir.exists(), (
            "default_dir must not exist before Collection()"
        )

        old_cwd = os.getcwd()
        os.chdir(temp_work_dir)

        try:
            collection = Collection(storage=temp_storage, catalog=temp_catalog)

            assert collection._storage == temp_storage
            assert collection._catalog == temp_catalog
        finally:
            os.chdir(old_cwd)


# class TestCollection_Get:
#     """
#     Collectionのget()メソッドをテストする。
#     - 正常系: 存在するidで取得成功
#     - 正常系: 存在しないidの場合はNoneを返す
#     """

#     def test_get_existing_filing(
#         self, temp_storage, temp_catalog, sample_filing
#     ) -> None:
#         """存在するFilingの取得テスト"""
#         collection = Collection(storage=temp_storage, catalog=temp_catalog)
#         filing, content = sample_filing

#         # Filing追加
#         collection.add(filing, content)

#         # 取得
#         retrieved = collection.get(filing.id)

#         assert retrieved is not None
#         assert retrieved.id == filing.id
#         assert retrieved.source == filing.source
#         assert retrieved.name == filing.name
#         assert retrieved.checksum == filing.checksum

#     def test_get_non_existing_filing(self, temp_storage, temp_catalog) -> None:
#         """存在しないFilingの取得テスト"""
#         collection = Collection(storage=temp_storage, catalog=temp_catalog)

#         # 存在しないidで取得
#         retrieved = collection.get("non_existing_id")

#         assert retrieved is None


# class TestCollection_Find:
#     """
#     Collectionのfind()メソッドをテストする。
#     - 正常系: exprなしで全件検索
#     - 正常系: exprを指定して条件検索
#     - 正常系: limit, offsetの動作確認
#     - 正常系: order_by, descの動作確認
#     """

#     def _create_multiple_filings(
#         self, collection: Collection, count: int
#     ) -> list[tuple[Filing, bytes]]:
#         """複数のFilingを作成してコレクションに追加"""
#         filings_data = []

#         for i in range(count):
#             content = f"test content {i}".encode()
#             checksum = hashlib.sha256(content).hexdigest()

#             filing = Filing(
#                 id=f"test_id_{i:03d}",
#                 source=f"source_{i % 3}",  # 3つのsourceに分散
#                 checksum=checksum,
#                 name=f"test_filing_{i}.txt",
#                 is_zip=i % 2 == 0,
#                 created_at=datetime(2024, 1, 1 + i, 12, 0, 0),
#             )

#             collection.add(filing, content)
#             filings_data.append((filing, content))

#         return filings_data

#     def test_find_all_filings(self, temp_storage, temp_catalog) -> None:
#         """全件検索のテスト"""
#         collection = Collection(storage=temp_storage, catalog=temp_catalog)

#         # 5つのFilingを追加
#         self._create_multiple_filings(collection, 5)

#         # 全件検索
#         results = collection.find()

#         assert len(results) == 5
#         assert all(isinstance(f, Filing) for f in results)

#     def test_find_with_expr(self, temp_storage, temp_catalog) -> None:
#         """条件検索のテスト"""
#         collection = Collection(storage=temp_storage, catalog=temp_catalog)

#         # 10件のFilingを追加
#         self._create_multiple_filings(collection, 10)

#         # source_1のFilingのみを検索
#         expr = Expr("source = ?", ["source_1"])
#         results = collection.find(expr=expr)

#         # source_1は 1, 4, 7 の3件
#         assert len(results) == 3
#         assert all(f.source == "source_1" for f in results)

#     def test_find_with_limit_offset(self, temp_storage, temp_catalog) -> None:
#         """limit、offsetのテスト"""
#         collection = Collection(storage=temp_storage, catalog=temp_catalog)

#         # 10件のFilingを追加
#         self._create_multiple_filings(collection, 10)

#         # limit=3で検索
#         results = collection.find(limit=3)
#         assert len(results) == 3

#         # offset=5, limit=3で検索
#         results_with_offset = collection.find(limit=3, offset=5)
#         assert len(results_with_offset) == 3

#         # 最初の結果と異なることを確認
#         assert results[0].id != results_with_offset[0].id

#     def test_find_with_order_by(self, temp_storage, temp_catalog) -> None:
#         """order_by、descのテスト"""
#         collection = Collection(storage=temp_storage, catalog=temp_catalog)

#         # 5件のFilingを追加
#         self._create_multiple_filings(collection, 5)

#         # created_at昇順で検索
#         results_asc = collection.find(order_by="created_at", desc=False)
#         assert results_asc[0].id == "test_id_000"
#         assert results_asc[-1].id == "test_id_004"

#         # created_at降順で検索（デフォルト）
#         results_desc = collection.find(order_by="created_at", desc=True)
#         assert results_desc[0].id == "test_id_004"
#         assert results_desc[-1].id == "test_id_000"

#     def test_find_empty_collection(self, temp_storage, temp_catalog) -> None:
#         """空のコレクションでの検索テスト"""
#         collection = Collection(storage=temp_storage, catalog=temp_catalog)

#         # 何も追加しない状態で検索
#         results = collection.find()

#         assert len(results) == 0
#         assert isinstance(results, list)
