from datetime import date

from fino_filing.core.error import FinoFilingException


class CollectorDateRangeValidationError(FinoFilingException, ValueError):
    """Edinet Date Range Validation Error"""

    def __init__(self, date_from: date, date_to: date):
        super().__init__(
            f"Date range validation error: date_from: {date_from}, date_to: {date_to}"
        )
        self.date_from = date_from
        self.date_to = date_to
