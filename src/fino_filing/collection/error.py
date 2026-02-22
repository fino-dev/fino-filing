from typing import Any

from fino_filing.core.error import FinoFilingException


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
