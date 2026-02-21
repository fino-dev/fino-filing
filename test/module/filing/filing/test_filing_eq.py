"""Filing の __eq__（等価判定）のテスト"""

from datetime import datetime
from typing import Annotated

from fino_filing import Filing
from fino_filing.filing.field import Field


class TestFiling_Eq:
    """
    Filing.__eq__ のテスト
    - 正常系: 同一クラス・同一データなら等しい
    - 正常系: 同一クラスでdictから生成したインスタンス同士の比較で等しい
    - 正常系: 同一クラス・異なるデータなら等しくない
    - 正常系: 同一クラスなら追加フィールドが同一値なら等しい
    - 正常系: 同一クラスなら追加フィールドが同一値が同じなら等しい
    - 正常系: 異なるクラスなら共通フィールドが同じでも等しくない
    - 正常系: default フィールドを保持するFiling同士の比較で等しい
    - 正常系: default フィールドを保持するFilingとインスタンス時に設定したFilingの比較で等しい



    """

    def test_eq_same_class_instance(self, datetime_now: datetime) -> None:
        """同一クラスのインスタンス同士の比較で等しい"""
        a = Filing(
            id="id1",
            source="src",
            checksum="c",
            name="n",
            is_zip=False,
            created_at=datetime_now,
        )
        b = Filing(
            id="id1",
            source="src",
            checksum="c",
            name="n",
            is_zip=False,
            created_at=datetime_now,
        )
        assert a == b
        assert b == a

    def test_eq_same_class_same_data(self, datetime_now: datetime) -> None:
        """同一クラス・同一データのとき等しい"""
        a = Filing(
            id="id1",
            source="src",
            checksum="c",
            name="n",
            is_zip=False,
            created_at=datetime_now,
        )
        b = Filing.from_dict(a.to_dict())
        assert a == b
        assert b == a

    def test_eq_same_class_different_data(self, datetime_now: datetime) -> None:
        """同一クラス・異なるデータのとき等しくない"""
        a = Filing(
            id="id1",
            source="src",
            checksum="c",
            name="n",
            is_zip=False,
            created_at=datetime_now,
        )
        b = Filing(
            id="id2",
            source="src",
            checksum="c",
            name="n",
            is_zip=False,
            created_at=datetime_now,
        )
        assert a != b
        assert b != a

    def test_eq_same_class_same_data_with_additional_field(
        self, datetime_now: datetime
    ) -> None:
        """同一クラス・同一データで追加フィールドが同一値なら等しい"""

        class ExtendedFiling(Filing):
            extra: Annotated[str, Field(description="Extra")]

        a = ExtendedFiling(
            id="id1",
            source="src",
            checksum="c",
            name="n",
            is_zip=False,
            created_at=datetime_now,
            extra="x",
        )
        b = ExtendedFiling(
            id="id1",
            source="src",
            checksum="c",
            name="n",
            is_zip=False,
            created_at=datetime_now,
            extra="x",
        )
        assert a == b
        assert b == a

    def test_eq_same_class_same_data_with_additional_field_different_value(
        self, datetime_now: datetime
    ) -> None:
        """同一クラス・同一データで追加フィールドが異なる値なら等しくない"""

        class ExtendedFiling(Filing):
            extra: Annotated[str, Field(description="Extra")]

        a = ExtendedFiling(
            id="id1",
            source="src",
            checksum="c",
            name="n",
            is_zip=False,
            created_at=datetime_now,
            extra="x",
        )
        b = ExtendedFiling(
            id="id1",
            source="src",
            checksum="c",
            name="n",
            is_zip=False,
            created_at=datetime_now,
            extra="y",
        )
        assert a != b
        assert b != a

    def test_eq_different_class_not_equal(self, datetime_now: datetime) -> None:
        """異なるクラスなら共通フィールドが同じでも等しくない"""

        class ExtendedFiling(Filing):
            source = "test_source"

        base = Filing(
            id="id1",
            source="test_source",
            checksum="c",
            name="n",
            is_zip=False,
            created_at=datetime_now,
        )
        extended = ExtendedFiling(
            id="id1",
            checksum="c",
            name="n",
            is_zip=False,
            created_at=datetime_now,
        )
        assert base != extended
        assert extended != base

    def test_eq_default_field_filing(self, datetime_now: datetime) -> None:
        """default フィールドを保持するFiling同士の比較で等しい"""

        class DefaultFieldFiling(Filing):
            checksum = "c"

        a = DefaultFieldFiling(
            id="id1",
            source="src",
            name="n",
            is_zip=False,
            created_at=datetime_now,
        )
        b = DefaultFieldFiling(
            id="id1",
            source="src",
            name="n",
            is_zip=False,
            created_at=datetime_now,
        )
        assert a == b
        assert b == a

    def test_eq_default_field_filing_different_value(
        self, datetime_now: datetime
    ) -> None:
        """default フィールドを保持するFiling同士の比較で異なる値なら等しくない"""

        class DefaultFieldFiling(Filing):
            checksum = "c"

        a = DefaultFieldFiling(
            id="id1",
            source="src",
            name="n",
            is_zip=False,
            created_at=datetime_now,
        )
        b = DefaultFieldFiling(
            id="id1",
            source="src",
            checksum="d",
            name="n",
            is_zip=False,
            created_at=datetime_now,
        )
        assert a != b
        assert b != a
