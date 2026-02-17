from fino_filing.core.error import FinoFilingException


class FilingValidationError(FinoFilingException, ValueError):
    """Filing の必須項目・型チェックに失敗した場合に送出する。"""

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
    """Immutableなフィールドを上書きしようとした場合に送出する。"""

    def __init__(
        self,
        message: str,
        fields: list[str] | None = None,
        errors: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.fields = fields or []
        self.errors = errors or []

    def __str__(self) -> str:
        return f"{self.message}\n " + "\n ".join(self.fields)
