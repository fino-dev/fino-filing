from datetime import datetime

import pytest

from fino_filing import Filing
from fino_filing.filing.error import FilingValidationError


class TestFiling_Initialize:
    """
    Filingのインスタンス化をテストする。
    - 正常系: すべてのフィールドが設定されている場合
    - 異常系: 必須フィールドが設定されていない場合
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
