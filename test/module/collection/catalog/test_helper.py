from datetime import datetime
from typing import Annotated

import pytest

from fino_filing import Catalog, Field, Filing


@pytest.mark.module
@pytest.mark.collection
class TestCatalog_Helper_get_table_column_names:
    """
    Catalog._get_table_column_names のテスト
    - テーブルに存在しているカラムを取得するために使用する
    """

    def test_get_table_column_names(self, temp_catalog: Catalog) -> None:
        """get_table_column_names は filings テーブルのカラム名をすべて返す（dataを含む）"""
        column_names = temp_catalog._get_table_column_names()

        assert column_names == [
            "id",
            "source",
            "checksum",
            "name",
            "is_zip",
            "format",
            "created_at",
            "_filing_class",
            "data",
        ]


@pytest.mark.module
@pytest.mark.collection
class TestCatalog_Helper_ensure_indexed_columns:
    """
    Catalog._ensure_indexed_columns のテスト
    - indexed=TrueのField classがテーブルに物理カラムとして存在していることを約束する
    ー 存在していない場合には作成される
    """

    def test_ensure_indexed_columns(self, temp_catalog: Catalog) -> None:
        """ensure_indexed_columns は indexed=TrueのField classがテーブルに物理カラムとして存在していることを約束する"""

        # 初期状態ではtickerが物理カラムに存在しない
        initial_columns = temp_catalog._get_table_column_names()
        assert "ticker" not in initial_columns

        class ExtendedFiling(Filing):
            ticker: Annotated[str, Field(indexed=True, description="Ticker")]

        # 追加のindexed=TrueのField classをensure_indexed_columns で ticker が物理カラムに追加される
        temp_catalog._ensure_indexed_columns(ExtendedFiling)
        final_columns = temp_catalog._get_table_column_names()
        assert "ticker" in final_columns


@pytest.mark.module
@pytest.mark.collection
class TestCatalog_Helper_data_only_dict:
    """
    Catalog._data_only_dict のテスト
    - 物理カラムに存在するキーを除いた辞書を返す（dataカラム）
    """

    def test_data_only_dict(self, temp_catalog: Catalog) -> None:
        """data_only_dict は物理カラムに存在するキーを除いた辞書を返す"""
        filing_dict = {
            "id": "test_id",
            "source": "test_source",
            "checksum": "test_checksum",
            "name": "test_name",
            "is_zip": False,
            "additional_field": "test_additional_field",
            "additional_field2": 100,
        }
        indexed_columns = {"id", "source", "checksum", "name", "is_zip"}

        data_only_dict = temp_catalog._data_only_dict(filing_dict, indexed_columns)
        assert data_only_dict == {
            "additional_field": "test_additional_field",
            "additional_field2": 100,
        }

    def test_data_only_dict_with_data_column_raises_error(
        self, temp_catalog: Catalog
    ) -> None:
        """data_only_dict の引数のindexed_columnsに data カラムを物理カラムとして含めた場合にはエラーを返す"""
        with pytest.raises(ValueError) as e:
            filing_dict = {
                "id": "test_id",
                "source": "test_source",
                "checksum": "test_checksum",
                "name": "test_name",
                "is_zip": False,
            }
            indexed_columns = {"id", "source", "checksum", "name", "is_zip", "data"}

            temp_catalog._data_only_dict(filing_dict, indexed_columns)

        assert str(e.value) == "dataカラムは物理カラムに含めることはできません"


@pytest.mark.module
@pytest.mark.collection
class TestCatalog_Helper_row_to_full_doc:
    """
    Catalog._row_to_full_doc のテスト
    - 1行（物理カラム）と data の JSON をマージして完全な辞書を返す ( dataカラムの値としてはJSON型であればそのままロードしてマージする )
    - dataカラムの値が空オブジェクトでも値なしとして許容される
    - dataカラムの値が単一の文字列や数値null（primitive）もjson型として許容される(RFC 8259）が、その場合はロジック上不正のため弾かれてエラーとなる
    - dataカラムの値がテーブル定義上not nullableのため、null値は許容されない
    """

    def test_row_to_full_doc(self, temp_catalog: Catalog) -> None:
        """
        row_to_full_doc は1行（物理カラム）と data の JSON をマージして完全な辞書を返す
        """

        columns = ["id", "source", "checksum", "name", "is_zip", "data"]
        row = (
            "test_id",
            "test_source",
            "test_checksum",
            "test_name",
            False,
            '{"additional_field": "test_additional_field", "additional_field2": 100}',
        )
        full_doc = temp_catalog._row_to_full_doc(columns, row)
        assert full_doc == {
            "id": "test_id",
            "source": "test_source",
            "checksum": "test_checksum",
            "name": "test_name",
            "is_zip": False,
            "additional_field": "test_additional_field",
            "additional_field2": 100,
        }

    def test_row_to_full_doc_with_no_data_column(self, temp_catalog: Catalog) -> None:
        """
        dataカラムの値が空オブジェクトでも値なしとして許容される
        """
        columns = ["id", "source", "checksum", "name", "is_zip", "data"]
        row = ("test_id", "test_source", "test_checksum", "test_name", False, "{}")
        full_doc = temp_catalog._row_to_full_doc(columns, row)

        assert full_doc == {
            "id": "test_id",
            "source": "test_source",
            "checksum": "test_checksum",
            "name": "test_name",
            "is_zip": False,
        }

    def test_row_to_full_doc_with_data_primitive_value_column_raises_error(
        self, temp_catalog: Catalog
    ) -> None:
        """
        dataカラムの値が単一の文字列や数値null（primitive）もjson型として許容される(RFC 8259）が、その場合はロジック上不正のため弾かれてエラーとなる
        """

        columns = ["id", "source", "checksum", "name", "is_zip", "data"]
        row = (
            "test_id",
            "test_source",
            "test_checksum",
            "test_name",
            False,
            "hoge",
        )
        full_doc = temp_catalog._row_to_full_doc(columns, row)

        assert full_doc == {
            "id": "test_id",
            "source": "test_source",
            "checksum": "test_checksum",
            "name": "test_name",
            "is_zip": False,
        }

    def test_row_to_full_doc_with_data_null_value_column_raises_error(
        self, temp_catalog: Catalog
    ) -> None:
        """
        dataカラムの値がnull値は許容されない
        """

        columns = ["id", "source", "checksum", "name", "is_zip", "data"]
        row = ("test_id", "test_source", "test_checksum", "test_name", False, None)
        full_doc = temp_catalog._row_to_full_doc(columns, row)
        assert full_doc == {
            "id": "test_id",
            "source": "test_source",
            "checksum": "test_checksum",
            "name": "test_name",
            "is_zip": False,
        }


@pytest.mark.module
@pytest.mark.collection
class TestCatalog_Helper_escape_sql_value:
    """
    Catalog._escape_sql_value のテスト
    - SQL のリテラルとして埋め込むために値をエスケープする
        None, bool, int, float, datetime, str の型に対して適切にエスケープされる
    """

    def test_escape_sql_value(
        self, temp_catalog: Catalog, datetime_now: datetime
    ) -> None:
        """
        escape_sql_value はSQL のリテラルとして埋め込むために値をエスケープする
        """
        assert temp_catalog._escape_sql_value(None) == "NULL"
        assert temp_catalog._escape_sql_value(True) == "TRUE"
        assert temp_catalog._escape_sql_value(False) == "FALSE"
        assert temp_catalog._escape_sql_value(100) == "100"
        assert temp_catalog._escape_sql_value(100.0) == "100.0"
        assert temp_catalog._escape_sql_value(datetime_now) == (
            "'" + datetime_now.isoformat() + "'"
        )
        assert temp_catalog._escape_sql_value("test_string") == "'test_string'"
        assert temp_catalog._escape_sql_value("test's") == "'test''s'"
