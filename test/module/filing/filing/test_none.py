from datetime import datetime

import pytest

from fino_filing.filing.error import FilingRequiredError
from fino_filing.filing.filing import Filing


class TestFiling_Initialize_ExplicitNone:
    """
    明示的にNoneを渡した場合の振る舞いをテストする。
    - 異常系: 必須フィールドに明示的にNoneを渡した場合
    - 正常系: default値を持つフィールドに明示的にNoneを渡した場合
    """

    def test_filing_init_with_explicit_none_for_required_field_failed(self) -> None:
        """必須フィールドに明示的にNoneを渡した場合はエラー"""
        with pytest.raises(FilingRequiredError) as fve:
            Filing(
                id=None,  # type: ignore
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                is_zip=True,
                format="zip",
                created_at=datetime.now(),
            )
        assert "id" in fve.value.fields

        with pytest.raises(FilingRequiredError) as fve:
            Filing(
                id="test_id",
                source=None,  # type: ignore
                checksum="test_checksum",
                name="test_name",
                is_zip=True,
                format="zip",
                created_at=datetime.now(),
            )
        assert "source" in fve.value.fields

        with pytest.raises(FilingRequiredError) as fve:
            Filing(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name=None,  # type: ignore
                is_zip=True,
                format="zip",
                created_at=datetime.now(),
            )
        assert "name" in fve.value.fields

    def test_filing_init_with_explicit_none_for_multiple_required_fields_failed(
        self,
    ) -> None:
        """複数の必須フィールドに明示的にNoneを渡した場合はエラー"""
        with pytest.raises(FilingRequiredError) as fve:
            Filing(
                id=None,  # type: ignore
                source=None,  # type: ignore
                checksum="test_checksum",
                name=None,  # type: ignore
                is_zip=True,
                format="zip",
                created_at=datetime.now(),
            )
        # すべてのNoneフィールドがエラーに含まれること
        assert "id" in fve.value.fields
        assert "source" in fve.value.fields
        assert "name" in fve.value.fields

    def test_filing_init_with_explicit_none_for_default_field_success(self) -> None:
        """default値を持つフィールドに明示的にNoneを渡した場合"""
        from typing import Annotated

        from fino_filing.filing.field import Field

        class DefaultFieldFiling(Filing):
            custom_field: Annotated[str, Field(description="Custom Field")] = (
                "default_value"
            )

        datetime_now = datetime.now()

        # default値を持つフィールドに明示的にNoneを渡す
        filing = DefaultFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            format="zip",
            created_at=datetime_now,
            custom_field=None,  # type: ignore
        )

        # Noneが設定される（default値は使われない）
        assert filing.custom_field is None
