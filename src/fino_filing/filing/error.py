class FilingValidationError(ValueError):
    """Filing の必須項目・型チェックに失敗した場合に送出する。"""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []

    def __str__(self) -> str:
        if not self.errors:
            return super().__str__()
        return f"{self.args[0]}\n " + "\n ".join(self.errors)
