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
        assert "created_at" in indexed_fields

        # 6つのフィールドが存在すること
        assert len(indexed_fields) == 6

    def test_get_indexed_fields_extended_filing_with_indexed(self) -> None:
        """indexedフィールドを追加した継承Filingの場合"""

        class ExtendedFiling(Filing):
            # indexed=True のフィールド
            ticker: Annotated[
                str, Field(indexed=True, description="Ticker Symbol")
            ]
            # indexed=False のフィールド
            revenue: Annotated[
                float, Field(indexed=False, description="Revenue")
            ]

        indexed_fields = ExtendedFiling.get_indexed_fields()

        # 基本Filingのフィールド + ticker
        assert "id" in indexed_fields
        assert "source" in indexed_fields
        assert "checksum" in indexed_fields
        assert "name" in indexed_fields
        assert "is_zip" in indexed_fields
        assert "created_at" in indexed_fields
        assert "ticker" in indexed_fields

        # revenue は indexed=False なので含まれない
        assert "revenue" not in indexed_fields

        # 7つのフィールドが存在すること
        assert len(indexed_fields) == 7

    def test_get_indexed_fields_extended_filing_without_indexed(self) -> None:
        """indexed=Falseのフィールドのみを追加した継承Filingの場合"""

        class ExtendedFiling(Filing):
            revenue: Annotated[
                float, Field(indexed=False, description="Revenue")
            ]
            profit: Annotated[
                float, Field(indexed=False, description="Profit")
            ]

        indexed_fields = ExtendedFiling.get_indexed_fields()

        # 基本Filingのフィールドのみ
        assert "id" in indexed_fields
        assert "source" in indexed_fields
        assert "checksum" in indexed_fields
        assert "name" in indexed_fields
        assert "is_zip" in indexed_fields
        assert "created_at" in indexed_fields

        # 追加フィールドは含まれない
        assert "revenue" not in indexed_fields
        assert "profit" not in indexed_fields

        # 6つのフィールドが存在すること（基本Filingと同じ）
        assert len(indexed_fields) == 6

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

        # 8つのindexedフィールドが存在すること
        assert len(indexed_fields) == 8

    def test_get_indexed_fields_unspecified_indexed(self) -> None:
        """indexedを指定しなかった場合（デフォルトFalse）"""

        class ExtendedFiling(Filing):
            # indexed を指定しない = デフォルトで False
            custom_field: Annotated[str, Field(description="Custom Field")]

        indexed_fields = ExtendedFiling.get_indexed_fields()

        # custom_field は indexed=False なので含まれない
        assert "custom_field" not in indexed_fields

        # 基本Filingと同じ6つのフィールド
        assert len(indexed_fields) == 6


class TestFiling_Repr:
    """
    Filing.__repr__() のテスト
    - 正常系: 文字列表現が正しいこと
    - 正常系: id, sourceが含まれること
    """

    def test_repr_success(self, datetime_now) -> None:
        """文字列表現が正しく生成されることを確認"""
        filing = Filing(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            created_at=datetime_now,
        )

        repr_str = repr(filing)

        assert "Filing" in repr_str
        assert "test_id" in repr_str
        assert "test_source" in repr_str
        assert repr_str == "Filing(id='test_id', source='test_source')"

    def test_repr_extended_filing(self, datetime_now) -> None:
        """継承Filingの文字列表現"""

        class ExtendedFiling(Filing):
            pass

        filing = ExtendedFiling(
            id="extended_id",
            source="extended_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
        )

        repr_str = repr(filing)

        # クラス名が正しいこと
        assert "ExtendedFiling" in repr_str
        assert "extended_id" in repr_str
        assert "extended_source" in repr_str
        assert repr_str == "ExtendedFiling(id='extended_id', source='extended_source')"
