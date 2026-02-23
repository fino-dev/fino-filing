from datetime import datetime
from typing import Annotated

import pytest

from fino_filing import Field, Filing
from fino_filing.filing.error import (
    FieldImmutableError,
    FilingRequiredError,
    FilingValidationError,
)


class TestFiling_Initialize:
    """
    Filingのインスタンス化をテストする。
    - 正常系: すべてのフィールドが設定されている場合
    - 異常系: 必須フィールドが設定されていない場合
    - 異常系: 型が一致しない場合
    - 異常系: core fieldは空文字は許容されない
    """

    def test_filing_init_success(self) -> None:
        filing = Filing(
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            format="zip",
        )

        assert len(filing.id) == 32
        assert filing.id.isalnum()  # sha256 hex
        assert filing.source == "test_source"
        assert filing.checksum == "test_checksum"
        assert filing.name == "test_name"
        assert filing.is_zip is True
        assert isinstance(filing.is_zip, bool)
        assert filing.format == "zip"
        assert isinstance(filing.created_at, datetime)

    def test_filing_id_generated_deterministically(self) -> None:
        """同一の source, name, is_zip, format で作成した場合、同じ id が生成される"""
        common = dict(
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
        )
        f1 = Filing(**common)
        f2 = Filing(**common)
        assert f1.id == f2.id
        assert len(f1.id) == 32

    def test_filing_id_generated_when_omitted(self) -> None:
        """id を渡さない場合、id が設定される"""
        f = Filing(
            source="s",
            checksum="c",
            name="n",
            is_zip=False,
            format="xbrl",
        )
        assert f.id is not None
        assert len(f.id) == 32

    def test_filing_id_includes_extended_indexed_metadata(self) -> None:
        """拡張 Filing ではユーザー追加フィールドが id のハッシュに含まれる"""
        class ExtendedFiling(Filing):
            doc_id: Annotated[str, Field(indexed=True, description="Doc ID")]

        base = dict(
            source="s",
            checksum="c",
            name="n",
            is_zip=False,
            format="xbrl",
        )
        f1 = ExtendedFiling(**base, doc_id="doc1")
        f2 = ExtendedFiling(**base, doc_id="doc1")
        f3 = ExtendedFiling(**base, doc_id="doc2")
        assert f1.id == f2.id
        assert f1.id != f3.id

    def test_filing_init_with_lack_field(self) -> None:
        # id / created_at は内部生成のため省略可能。source, checksum, name, is_zip, format は必須。
        with pytest.raises(FilingRequiredError) as fve:
            Filing(
                checksum="test_checksum",
                name="test_name",
                is_zip=True,
                format="zip",
            )
        assert fve.value.fields == ["source"]

        with pytest.raises(FilingRequiredError) as fve:
            Filing(
                source="test_source",
                name="test_name",
                is_zip=True,
                format="zip",
            )
        assert fve.value.fields == ["checksum"]

        with pytest.raises(FilingRequiredError) as fve:
            Filing(
                source="test_source",
                checksum="test_checksum",
                is_zip=True,
                format="zip",
            )
        assert fve.value.fields == ["name"]

        with pytest.raises(FilingRequiredError) as fve:
            Filing(
                source="test_source",
                checksum="test_checksum",
                is_zip=True,
                format="zip",
            )
        assert fve.value.fields == ["name"]

        with pytest.raises(FilingRequiredError) as fve:
            Filing(
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                format="zip",
            )
        assert fve.value.fields == ["is_zip"]

    def test_filing_init_with_invalid_field_failed(self) -> None:
        with pytest.raises(FilingValidationError) as fve:
            Filing(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name=123,
                is_zip="test_is_zip",
                format="zip",
                created_at=123,
            )
        assert fve.value.fields == ["name", "is_zip", "created_at"]

    def test_filing_init_with_core_field_empty_failed(self) -> None:
        with pytest.raises(FilingValidationError) as fve:
            Filing(
                id="",
                source="",
                checksum="",
                name="",
                is_zip=True,
                format="",
                created_at=datetime.now(),
            )
        assert fve.value.fields == ["id", "source", "checksum", "name", "format"]


class TestFiling_Initialize_ImmutableField:
    """
    Filingのインスタンス化のimmutableフィールドの振る舞いをテストする。
    - 正常形: immutableフィールドを設定された値は上書き変更できる / 異常形: immutableフィールドを設定されていない値は上書き変更できない
    """

    def test_filing_init_with_immutable_field_success(self) -> None:
        f = Filing(
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            format="zip",
        )
        generated_id = f.id
        generated_created_at = f.created_at
        assert generated_id
        assert generated_created_at is not None
        assert f.source == "test_source"
        assert f.checksum == "test_checksum"
        assert f.name == "test_name"
        assert f.is_zip is True
        assert f.created_at == generated_created_at

        # checksum, is_zipはmutableのため上書き変更できる
        f.checksum = "overwrite_checksum"
        f.is_zip = False

        assert f.checksum == "overwrite_checksum"
        assert f.is_zip is False

        # id, source, name, created_atはimmutableのため初期化後に変更できない
        with pytest.raises(FieldImmutableError) as fva:
            f.id = "overwrite_id"
        assert fva.value.field == "id"

        with pytest.raises(FieldImmutableError) as fva:
            f.source = "overwrite_source"
        assert fva.value.field == "source"

        with pytest.raises(FieldImmutableError) as fva:
            f.name = "overwrite_name"
        assert fva.value.field == "name"

        with pytest.raises(FieldImmutableError) as fva:
            f.created_at = datetime.now()
        assert fva.value.field == "created_at"
