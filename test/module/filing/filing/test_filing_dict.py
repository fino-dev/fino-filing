from datetime import datetime
from typing import Annotated, Any

import pytest

from fino_filing import Filing
from fino_filing.filing.error import FieldRequiredError, FilingValidationError
from fino_filing.filing.field import Field


class TestFiling_ToDict:
    """
    Filing.to_dict() のテスト
    - 正常系: すべてのフィールドが辞書化されること
    - 正常系: datetimeがISO文字列に変換されること
    - 正常系: default値のみのインスタンスの変換
    """

    def test_to_dict_success(self) -> None:
        """すべてのフィールドが正しく辞書化されることを確認"""
        datetime_now = datetime.now()

        filing = Filing(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            created_at=datetime_now,
        )

        result = filing.to_dict()

        assert result["id"] == "test_id"
        assert result["source"] == "test_source"
        assert result["checksum"] == "test_checksum"
        assert result["name"] == "test_name"
        assert result["is_zip"] is True
        assert result["created_at"] == datetime_now.isoformat()

    def test_to_dict_datetime_conversion(self) -> None:
        """datetimeがISO文字列に変換されることを確認"""
        datetime_now = datetime(2024, 1, 15, 10, 30, 45, 123456)

        filing = Filing(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
        )

        result = filing.to_dict()

        # ISO形式の文字列であることを確認
        assert isinstance(result["created_at"], str)
        assert result["created_at"] == "2024-01-15T10:30:45.123456"

    def test_to_dict_with_default_values(self) -> None:
        """default値を持つフィールドが正しく辞書化されることを確認"""

        class DefaultFieldFiling(Filing):
            checksum = "default_checksum"
            is_zip = False

        datetime_now = datetime.now()
        filing = DefaultFieldFiling(
            id="test_id",
            source="test_source",
            name="test_name",
            created_at=datetime_now,
        )

        result = filing.to_dict()

        assert result["checksum"] == "default_checksum"
        assert result["is_zip"] is False

    def test_to_dict_with_additional_fields(self) -> None:
        """追加フィールドを持つ継承Filingの辞書化"""

        class ExtendedFiling(Filing):
            revenue: Annotated[float, Field(description="Revenue")]

        datetime_now = datetime.now()
        filing = ExtendedFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            created_at=datetime_now,
            revenue=1000000.0,
        )

        result = filing.to_dict()

        assert result["revenue"] == 1000000.0
        assert result["id"] == "test_id"


class TestFiling_FromDict:
    """
    Filing.from_dict() のテスト
    - 正常系: 辞書からFilingインスタンスが作成されること
    - 正常系: ISO文字列がdatetimeに変換されること
    - 異常系: 必須フィールドが不足している場合
    - 異常系: 型が一致しない場合
    """

    def test_from_dict_success(self) -> None:
        """辞書から正しくFilingインスタンスが作成されることを確認"""
        datetime_now = datetime.now()
        data = {
            "id": "test_id",
            "source": "test_source",
            "checksum": "test_checksum",
            "name": "test_name",
            "is_zip": True,
            "created_at": datetime_now,
        }

        filing = Filing.from_dict(data)

        assert filing.id == "test_id"
        assert filing.source == "test_source"
        assert filing.checksum == "test_checksum"
        assert filing.name == "test_name"
        assert filing.is_zip is True
        assert filing.created_at == datetime_now

    def test_from_dict_datetime_conversion(self) -> None:
        """ISO文字列がdatetimeに変換されることを確認"""
        data = {
            "id": "test_id",
            "source": "test_source",
            "checksum": "test_checksum",
            "name": "test_name",
            "is_zip": False,
            "created_at": "2024-01-15T10:30:45.123456",
        }

        filing = Filing.from_dict(data)

        assert isinstance(filing.created_at, datetime)
        assert filing.created_at == datetime(2024, 1, 15, 10, 30, 45, 123456)

    def test_from_dict_with_missing_fields_failed(self) -> None:
        """必須フィールドが不足している場合はエラー"""
        data = {
            "id": "test_id",
            "source": "test_source",
            "checksum": "test_checksum",
            # name, is_zip, created_at が不足
        }

        with pytest.raises(FieldRequiredError) as fve:
            Filing.from_dict(data)

        assert "name" in fve.value.fields
        assert "is_zip" in fve.value.fields
        assert "created_at" in fve.value.fields

    def test_from_dict_with_invalid_type_failed(self) -> None:
        """型が一致しない場合はエラー"""
        data = {
            "id": "test_id",
            "source": "test_source",
            "checksum": "test_checksum",
            "name": 123,  # str ではなく int
            "is_zip": "invalid",  # bool ではなく str
            "created_at": "2024-01-15T10:30:45",
        }

        with pytest.raises(FilingValidationError) as fve:
            Filing.from_dict(data)

        assert "name" in fve.value.fields
        assert "is_zip" in fve.value.fields

    def test_from_dict_with_extended_filing(self) -> None:
        """継承Filingの辞書からの復元"""

        class ExtendedFiling(Filing):
            revenue: Annotated[float, Field(description="Revenue")]

        data: dict[str, Any] = {
            "id": "test_id",
            "source": "test_source",
            "checksum": "test_checksum",
            "name": "test_name",
            "is_zip": True,
            "created_at": "2024-01-15T10:30:45",
            "revenue": 1000000.0,
        }

        filing = ExtendedFiling.from_dict(data)

        assert filing.revenue == 1000000.0
        assert filing.id == "test_id"


class TestFiling_ToDict_FromDict_RoundTrip:
    """
    to_dict() と from_dict() のラウンドトリップテスト
    - 正常系: to_dict() -> from_dict() で元のデータが復元されること
    """

    def test_roundtrip_success(self) -> None:
        """to_dict() -> from_dict() で元のデータが復元されることを確認"""
        datetime_now = datetime(2024, 1, 15, 10, 30, 45, 123456)

        original = Filing(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            created_at=datetime_now,
        )

        # to_dict() -> from_dict()
        data = original.to_dict()
        restored = Filing.from_dict(data)

        # すべてのフィールドが一致することを確認
        assert restored.id == original.id
        assert restored.source == original.source
        assert restored.checksum == original.checksum
        assert restored.name == original.name
        assert restored.is_zip == original.is_zip
        assert restored.format == original.format
        assert restored.created_at == original.created_at

    def test_roundtrip_preserves_format(self) -> None:
        """format を指定した Filing は to_dict() -> from_dict() で format が復元される"""
        datetime_now = datetime(2024, 1, 15, 10, 30, 45)
        original = Filing(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="report.pdf",
            is_zip=False,
            format="pdf",
            created_at=datetime_now,
        )
        data = original.to_dict()
        assert data.get("format") == "pdf"
        restored = Filing.from_dict(data)
        assert restored.format == "pdf"
        assert restored.id == original.id

    def test_roundtrip_with_extended_filing(self) -> None:
        """継承Filingのラウンドトリップ"""

        class ExtendedFiling(Filing):
            revenue: Annotated[float, Field(description="Revenue")]
            period_start: Annotated[datetime, Field(description="Period Start")]

        datetime_now = datetime(2024, 1, 15, 10, 30, 45)
        period_start = datetime(2024, 1, 1, 0, 0, 0)

        original = ExtendedFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
            revenue=1000000.0,
            period_start=period_start,
        )

        # to_dict() -> from_dict()
        data = original.to_dict()
        restored = ExtendedFiling.from_dict(data)

        # すべてのフィールドが一致することを確認
        assert restored.revenue == original.revenue
        assert restored.period_start == original.period_start
        assert restored.id == original.id

    def test_roundtrip_with_default_values(self) -> None:
        """default値を持つFilingのラウンドトリップ"""

        class DefaultFieldFiling(Filing):
            checksum = "default_checksum"

        datetime_now = datetime.now()

        original = DefaultFieldFiling(
            id="test_id",
            source="test_source",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
        )

        # to_dict() -> from_dict()
        data = original.to_dict()
        restored = DefaultFieldFiling.from_dict(data)

        assert restored.checksum == original.checksum
        assert restored.id == original.id
