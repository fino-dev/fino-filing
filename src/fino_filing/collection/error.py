from fino_filing.core.error import FinoFilingException


class CollectionChecksumMismatchError(FinoFilingException, ValueError):
    """Checksum mismatch error"""

    def __init__(
        self,
        filing_id: str,
        filing_name: str,
        actual_checksum: str,
        expected_checksum: str,
    ):
        super().__init__(
            f"Checksum mismatch filing id: {filing_id}, filing name: {filing_name}, actual checksum: {actual_checksum}, expected checksum: {expected_checksum}"
        )
        self.filing_id = filing_id
        self.filing_name = filing_name
        self.actual_checksum = actual_checksum
        self.expected_checksum = expected_checksum
