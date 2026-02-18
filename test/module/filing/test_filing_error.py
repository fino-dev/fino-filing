import pytest

from fino_filing.filing.error import (
    FieldImmutableError,
    FieldValidationError,
    FilingImmutableError,
    FilingValidationError,
)


class TestFieldValidationError:
    """
    FieldValidationErrorの振る舞いテスト
    """

    def test_filing_error_message(self) -> None:
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
    FieldImmutableErrorの振る舞いテスト
    """

    def test_field_immutable_error_message(self) -> None:
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
    FilingValidationErrorの振る舞いテスト
    """

    def test_filing_validation_error_message(self) -> None:
        with pytest.raises(FilingValidationError) as e:
            raise FilingValidationError(
                "test message",
                errors=["test_error_1", "test_error_2"],
                fields=["test_field_1", "test_field_2"],
            )
        assert e.value.message == "[Fino Filing] test message"
        assert e.value.errors == ["test_error_1", "test_error_2"]
        assert e.value.fields == ["test_field_1", "test_field_2"]

    def test_filing_validation_error_str_with_errors(self) -> None:
        with pytest.raises(FilingValidationError) as e:
            raise FilingValidationError(
                "test message",
                errors=["test_error_1", "test_error_2"],
                fields=["test_field_1", "test_field_2"],
            )
        assert (
            str(e.value) == "[Fino Filing] test message\n test_error_1\n test_error_2"
        )

    def test_filing_validation_error_str_without_errors(self) -> None:
        with pytest.raises(FilingValidationError) as e:
            raise FilingValidationError(
                "test message",
                fields=["test_field_1", "test_field_2"],
            )
        assert str(e.value) == "[Fino Filing] test message"


class TestFilingImmutableError:
    """
    FilingImmutableErrorの振る舞いテスト
    """

    def test_filing_immutable_error_message(self) -> None:
        with pytest.raises(FilingImmutableError) as e:
            raise FilingImmutableError(
                "test message",
                errors=["test_error_1", "test_error_2"],
                fields=["test_field_1", "test_field_2"],
            )
        assert e.value.message == "[Fino Filing] test message"
        assert e.value.errors == ["test_error_1", "test_error_2"]
        assert e.value.fields == ["test_field_1", "test_field_2"]

    def test_filing_immutable_error_str_with_errors(self) -> None:
        with pytest.raises(FilingImmutableError) as e:
            raise FilingImmutableError(
                "test message",
                errors=["test_error_1", "test_error_2"],
                fields=["test_field_1", "test_field_2"],
            )

        assert (
            str(e.value) == "[Fino Filing] test message\n test_error_1\n test_error_2"
        )

    def test_filing_immutable_error_str_without_errors(self) -> None:
        with pytest.raises(FilingImmutableError) as e:
            raise FilingImmutableError(
                "test message",
                fields=["test_field_1", "test_field_2"],
            )
        assert str(e.value) == "[Fino Filing] test message"
