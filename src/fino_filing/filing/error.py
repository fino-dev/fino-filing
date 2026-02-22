from typing import Any

from fino_filing.core.error import FinoFilingException


class FieldValidationError(FinoFilingException, ValueError):
    """Field Validation Error"""

    def __init__(
        self,
        message: str,
        field: str,
        expected_type: type,
        actual_type: type,
    ) -> None:
        super().__init__(message)
        self.field = field
        self.expected_type = expected_type
        self.actual_type = actual_type


class FieldImmutableError(FinoFilingException, ValueError):
    """Field Immutable Error"""

    def __init__(
        self,
        message: str,
        field: str,
        current_value: Any,
        attempt_value: Any,
    ) -> None:
        super().__init__(message)
        self.field = field
        self.current_value = current_value
        self.attempt_value = attempt_value


class FilingValidationError(FinoFilingException, ValueError):
    """Filing Validation Error"""

    def __init__(
        self,
        message: str,
        errors: list[str] | None = None,
        fields: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        # message will be parent valueError's args[0]
        self.errors = errors or []
        # エラーがあったフィールド名のリスト
        self.fields = fields or []

    def __str__(self) -> str:
        if not self.errors:
            return super().__str__()
        return f"{self.message}\n " + "\n ".join(self.errors)


class FilingImmutableError(FinoFilingException, ValueError):
    """Filing Immutable Error"""

    def __init__(
        self,
        message: str,
        errors: list[str] | None = None,
        fields: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.errors = errors or []
        self.fields = fields or []

    def __str__(self) -> str:
        if not self.errors:
            return super().__str__()
        return f"{self.message}\n " + "\n ".join(self.errors)


class FilingRequiredError(FinoFilingException, ValueError):
    """
    Required Field Error
    Prohibited to set None to required fields.
    """

    def __init__(
        self,
        message: str,
        errors: list[str] | None = None,
        fields: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.errors = errors or []
        self.fields = fields or []

    def __str__(self) -> str:
        if not self.errors:
            return super().__str__()
        return f"{self.message}\n " + "\n ".join(self.errors)
