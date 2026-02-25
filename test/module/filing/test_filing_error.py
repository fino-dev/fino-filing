from typing import Any, Type

import pytest

from fino_filing.filing.error import (
    FieldImmutableError,
    FieldValidationError,
    FilingImmutableError,
    FilingRequiredError,
    FilingValidationError,
)


class TestFieldValidationError:
    """
    FieldValidationError. 観点: 異常系（例外の属性が仕様どおりであること）
    """

    def test_filing_error_message(self) -> None:
        """仕様: 型不正時に field, expected_type, actual_type を含む。検証: 例外型と message, field, expected_type, actual_type"""
        with pytest.raises(FieldValidationError) as e:
            raise FieldValidationError(
                "test message", field="test_field", expected_type=int, actual_type=str
            )
        assert e.value.message == "[Fino Filing] test message"
        assert e.value.field == "test_field"
        assert e.value.expected_type == int  # noqa: E721
        assert e.value.actual_type == str  # noqa: E721


class TestFieldImmutableError:
    """
    FieldImmutableError. 観点: 異常系（例外の属性が仕様どおりであること）
    """

    def test_field_immutable_error_message(self) -> None:
        """仕様: immutable 変更試行時に field, current_value, attempt_value を含む。検証: 例外型と各属性"""
        with pytest.raises(FieldImmutableError) as e:
            raise FieldImmutableError(
                "test message", field="test_field", current_value=1, attempt_value=2
            )
        assert e.value.message == "[Fino Filing] test message"
        assert e.value.field == "test_field"
        assert e.value.current_value == 1
        assert e.value.attempt_value == 2


class TestFilingValidationError:
    """
    FilingValidationError. 観点: 異常系（複数フィールドのバリデーションエラー）
    """

    def test_filing_validation_error_message(self) -> None:
        """仕様: errors と fields を持つ。検証: 例外型と message, errors, fields"""
        with pytest.raises(FilingValidationError) as e:
            raise FilingValidationError(
                "test message",
                errors=["test_error_1", "test_error_2"],
                fields=["test_field_1", "test_field_2"],
            )
        assert e.value.message == "[Fino Filing] test message"
        assert e.value.errors == ["test_error_1", "test_error_2"]
        assert e.value.fields == ["test_field_1", "test_field_2"]


class TestFilingImmutableError:
    """
    FilingImmutableError. 観点: 異常系（複数フィールドの immutable 違反）
    """

    def test_filing_immutable_error_message(self) -> None:
        """仕様: errors と fields を持つ。検証: 例外型と message, errors, fields"""
        with pytest.raises(FilingImmutableError) as e:
            raise FilingImmutableError(
                "test message",
                errors=["test_error_1", "test_error_2"],
                fields=["test_field_1", "test_field_2"],
            )
        assert e.value.message == "[Fino Filing] test message"
        assert e.value.errors == ["test_error_1", "test_error_2"]
        assert e.value.fields == ["test_field_1", "test_field_2"]


class TestFilingRequiredError:
    """
    FilingRequiredError. 観点: 異常系（必須フィールド欠損）
    """

    def test_filing_core_field_error_message(self) -> None:
        """仕様: errors と fields を持つ。検証: 例外型と message, errors, fields"""
        with pytest.raises(FilingRequiredError) as e:
            raise FilingRequiredError(
                "test message",
                errors=["error_1", "error_2"],
                fields=["field_1", "field_2"],
            )
        assert e.value.message == "[Fino Filing] test message"
        assert e.value.errors == ["error_1", "error_2"]
        assert e.value.fields == ["field_1", "field_2"]


class TestFilingError_Str_Parametrized:
    """FilingValidationError / FilingImmutableError / FilingRequiredError の str(). 観点: 異常系（parametrize）"""

    @pytest.mark.parametrize(
        "exc_class,kwargs,expected",
        [
            (
                FilingValidationError,
                {
                    "errors": ["test_error_1", "test_error_2"],
                    "fields": ["test_field_1", "test_field_2"],
                },
                "[Fino Filing] test message\n test_error_1\n test_error_2",
            ),
            (
                FilingImmutableError,
                {
                    "errors": ["test_error_1", "test_error_2"],
                    "fields": ["test_field_1", "test_field_2"],
                },
                "[Fino Filing] test message\n test_error_1\n test_error_2",
            ),
            (
                FilingRequiredError,
                {"errors": ["error_1", "error_2"], "fields": ["field_1", "field_2"]},
                "[Fino Filing] test message\n error_1\n error_2",
            ),
        ],
    )
    def test_error_str_with_errors(
        self,
        exc_class: Type[Any],
        kwargs: dict[str, Any],
        expected: str,
    ) -> None:
        """仕様: str() で errors が改行区切りで含まれる。検証: str(e.value)"""
        with pytest.raises(exc_class) as e:
            raise exc_class("test message", **kwargs)
        assert str(e.value) == expected

    @pytest.mark.parametrize(
        "exc_class,kwargs",
        [
            (FilingValidationError, {"fields": ["test_field_1", "test_field_2"]}),
            (FilingImmutableError, {"fields": ["test_field_1", "test_field_2"]}),
            (FilingRequiredError, {"fields": ["id", "source"]}),
        ],
    )
    def test_error_str_without_errors(
        self, exc_class: Type[Any], kwargs: dict[str, Any]
    ) -> None:
        """仕様: errors 未指定時は message のみ。検証: str(e.value) が message と一致"""
        with pytest.raises(exc_class) as e:
            raise exc_class("test message", **kwargs)
        assert str(e.value) == "[Fino Filing] test message"
