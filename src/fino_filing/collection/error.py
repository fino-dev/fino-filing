from typing import Any

from fino_filing.core.error import FinoFilingException
from fino_filing.filing.filing import Filing

"""
Collection Errors
"""


class CollectionChecksumMismatchError(FinoFilingException, ValueError):
    """Checksum mismatch error"""

    def __init__(
        self,
        filing_id: str,
        actual_checksum: str,
        expected_checksum: str,
    ):
        super().__init__(
            f"Checksum mismatch filing id: {filing_id}, actual checksum: {actual_checksum}, expected checksum: {expected_checksum}"
        )
        self.filing_id = filing_id
        self.actual_checksum = actual_checksum
        self.expected_checksum = expected_checksum


"""
Locator Errors
"""


class LocatorPathResolutionError(FinoFilingException, ValueError):
    """Locator path resolution error"""

    def __init__(self, filing: Filing | None):
        super().__init__(f"Locator did not resolve path for filing: {filing}")
        self.filing = filing


"""
Catalog Errors
"""


class CatalogRequiredValueError(FinoFilingException, ValueError):
    """Required value error"""

    def __init__(
        self,
        field: str,
        actual_value: Any,
    ):
        super().__init__(
            f"Required field '{field}' is missing or empty: value: {actual_value}"
        )
        self.field = field
        self.value = actual_value


class CatalogAlreadyExistsError(FinoFilingException, ValueError):
    """Already exists in catalog error"""

    def __init__(
        self,
        filing_id: str,
    ):
        super().__init__(f"Filing id: {filing_id} already exists in catalog")
        self.filing_id = filing_id


class CatalogExprTypeError(FinoFilingException, TypeError):
    """Expr type error"""

    def __init__(self, expr: Any):
        super().__init__(f"Expr must be Expr or None, not {type(expr).__name__}")
        self.expr = expr
