from datetime import datetime

import pytest

from fino_filing import Filing
from fino_filing.filing.error import FilingValidationError


class TestFiling_Initialize:
    """
    Filingのインスタンス化をテストする。
    - 正常系: すべてのフィールドが設定されている場合
    - 異常系: 必須フィールドが設定されていない場合
    - 異常系: 型が一致しない場合
    """

    def test_filing_init_success(self) -> None:
        datetime_now = datetime.now()

        filing = Filing(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            created_at=datetime_now,
        )

        assert filing.id == "test_id"
        assert filing.source == "test_source"
        assert filing.checksum == "test_checksum"
        assert filing.name == "test_name"
        assert filing.is_zip is True
        assert filing.created_at == datetime_now

    def test_filing_init_with_lack_field(self) -> None:
        with pytest.raises(FilingValidationError) as fve:
            # instance without id
            Filing(
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                is_zip=True,
                created_at=datetime.now(),
            )
        assert fve.value.fields == ["id"]

        with pytest.raises(FilingValidationError) as fve:
            # instance without source
            Filing(
                id="test_id",
                checksum="test_checksum",
                name="test_name",
                is_zip=True,
                created_at=datetime.now(),
            )

        assert fve.value.fields == ["source"]

        with pytest.raises(FilingValidationError) as fve:
            # instance without checksum
            Filing(
                id="test_id",
                source="test_source",
                name="test_name",
                is_zip=True,
                created_at=datetime.now(),
            )
        assert fve.value.fields == ["checksum"]

        with pytest.raises(FilingValidationError) as fve:
            # instance without name
            Filing(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                is_zip=True,
                created_at=datetime.now(),
            )
        assert fve.value.fields == ["name"]

        with pytest.raises(FilingValidationError) as fve:
            # instance without is_zip
            Filing(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                created_at=datetime.now(),
            )
        assert fve.value.fields == ["is_zip"]

        with pytest.raises(FilingValidationError) as fve:
            # instance with invalid created_at
            Filing(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                is_zip=True,
            )
        assert fve.value.fields == ["created_at"]

    def test_filing_init_with_invalid_field_failed(self) -> None:
        with pytest.raises(FilingValidationError) as fve:
            Filing(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name=123,
                is_zip="test_is_zip",
                created_at=123,
            )
        assert fve.value.fields == ["name"]


class TestFiling_Initialize_ImmutableField:
    """
    Filingのインスタンス化のimmutableフィールドの振る舞いをテストする。
    - 正常形: immutableフィールドを設定された値は上書き変更できる / 異常形: immutableフィールドを設定されていない値は上書き変更できない
    """

    def test_filing_init_with_immutable_field_success(
        self, datetime_now: datetime
    ) -> None:
        f = Filing(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            created_at=datetime_now,
        )
        assert f.id == "test_id"
        assert f.source == "test_source"
        assert f.checksum == "test_checksum"
        assert f.name == "test_name"
        assert f.is_zip is True
        assert f.created_at == datetime_now

        # checksum, is_zipはmutableのため上書き変更できる
        f.checksum = "overwrite_checksum"
        f.is_zip = False

        assert f.checksum == "overwrite_checksum"
        assert f.is_zip is False

        # id, source, name,create_atはimmutableのため初期化後に変更できない
        with pytest.raises(FilingValidationError) as fva:
            f.id = "overwrite_id"
        assert fva.value.fields == ["id"]

        with pytest.raises(FilingValidationError) as fva:
            f.source = "overwrite_source"
        assert fva.value.fields == ["source"]

        with pytest.raises(FilingValidationError) as fva:
            f.name = "overwrite_name"
        assert fva.value.fields == ["name"]

        with pytest.raises(FilingValidationError) as fva:
            f.created_at = datetime.now()
        assert fva.value.fields == ["created_at"]
