from datetime import datetime
from typing import Annotated

from fino_filing import Filing
from fino_filing.filing.field import Field


class TestFiling_GetIndexedFields:
    """
    Filing.get_indexed_fields() のテスト
    - 正常系: 基本Filingのindexedフィールド一覧が取得できること
    - 正常系: 継承してフィールド追加した場合のindexedフィールド一覧
    - 正常系: non-indexedフィールドは含まれないこと
    """

    def test_get_indexed_fields_base_filing(self) -> None:
        """基本Filingのindexedフィールドがすべて取得できることを確認"""
        indexed_fields = Filing.get_indexed_fields()

        # 基本Filingのすべてのフィールドはindexed=True
        assert "id" in indexed_fields
        assert "source" in indexed_fields
        assert "checksum" in indexed_fields
        assert "name" in indexed_fields
        assert "is_zip" in indexed_fields
        assert "format" in indexed_fields
        assert "created_at" in indexed_fields

        # 7つのフィールドが存在すること
        assert len(indexed_fields) == 7

    def test_get_indexed_fields_extended_filing_with_indexed(self) -> None:
        """indexedフィールドを追加した継承Filingの場合"""

        class ExtendedFiling(Filing):
            # indexed=True のフィールド
            ticker: Annotated[str, Field(indexed=True, description="Ticker Symbol")]
            # indexed=False のフィールド
            revenue: Annotated[float, Field(indexed=False, description="Revenue")]

        indexed_fields = ExtendedFiling.get_indexed_fields()

        # 基本Filingのフィールド + ticker
        assert "id" in indexed_fields
        assert "source" in indexed_fields
        assert "checksum" in indexed_fields
        assert "name" in indexed_fields
        assert "is_zip" in indexed_fields
        assert "format" in indexed_fields
        assert "created_at" in indexed_fields
        assert "ticker" in indexed_fields

        # revenue は indexed=False なので含まれない
        assert "revenue" not in indexed_fields

        # 8つのフィールドが存在すること
        assert len(indexed_fields) == 8

    def test_get_indexed_fields_extended_filing_without_indexed(self) -> None:
        """indexed=Falseのフィールドのみを追加した継承Filingの場合"""

        class ExtendedFiling(Filing):
            revenue: Annotated[float, Field(indexed=False, description="Revenue")]
            profit: Annotated[float, Field(indexed=False, description="Profit")]

        indexed_fields = ExtendedFiling.get_indexed_fields()

        # 基本Filingのフィールドのみ
        assert "id" in indexed_fields
        assert "source" in indexed_fields
        assert "checksum" in indexed_fields
        assert "name" in indexed_fields
        assert "is_zip" in indexed_fields
        assert "format" in indexed_fields
        assert "created_at" in indexed_fields

        # 追加フィールドは含まれない
        assert "revenue" not in indexed_fields
        assert "profit" not in indexed_fields

        # 7つのフィールドが存在すること（基本Filingと同じ）
        assert len(indexed_fields) == 7

    def test_get_indexed_fields_multiple_inheritance(self) -> None:
        """多段階継承の場合"""

        class FirstExtended(Filing):
            field1: Annotated[str, Field(indexed=True, description="Field 1")]

        class SecondExtended(FirstExtended):
            field2: Annotated[str, Field(indexed=True, description="Field 2")]
            field3: Annotated[str, Field(indexed=False, description="Field 3")]

        indexed_fields = SecondExtended.get_indexed_fields()

        # すべての親クラスのindexedフィールドが含まれること
        assert "id" in indexed_fields
        assert "field1" in indexed_fields
        assert "field2" in indexed_fields

        # indexed=False のフィールドは含まれない
        assert "field3" not in indexed_fields

        # 9つのindexedフィールドが存在すること（基本7 + field1 + field2）
        assert len(indexed_fields) == 9

    def test_get_indexed_fields_unspecified_indexed(self) -> None:
        """indexedを指定しなかった場合（デフォルトFalse）"""

        class ExtendedFiling(Filing):
            # indexed を指定しない = デフォルトで False
            custom_field: Annotated[str, Field(description="Custom Field")]

        indexed_fields = ExtendedFiling.get_indexed_fields()

        # custom_field は indexed=False なので含まれない
        assert "custom_field" not in indexed_fields

        # 基本Filingと同じ7つのフィールド
        assert len(indexed_fields) == 7


class TestFiling_Repr:
    """
    Filing.__repr__() のテスト
    - 正常系: クラス名が含まれていること・すべてのフィールドが含まれること
    - 正常系: 継承クラスでも同様に正しく生成されること
    """

    def test_repr_success(self, datetime_now: datetime) -> None:
        """文字列表現が正しく生成されることを確認"""
        filing = Filing(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            format="zip",
            created_at=datetime_now,
        )

        repr_str = repr(filing)

        assert "Filing" in repr_str
        # すべてのフィールドが含まれること
        assert "id" in repr_str
        assert "source" in repr_str
        assert "checksum" in repr_str
        assert "name" in repr_str
        assert "is_zip" in repr_str
        assert "format" in repr_str
        assert "created_at" in repr_str

    def test_repr_extended_filing(self, datetime_now: datetime) -> None:
        """継承Filingの文字列表現"""

        class ExtendedFiling(Filing):
            pass

        filing = ExtendedFiling(
            id="extended_id",
            source="extended_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )

        repr_str = repr(filing)

        # クラス名が正しいこと
        assert "ExtendedFiling" in repr_str
        assert "extended_id" in repr_str
        assert "extended_source" in repr_str
