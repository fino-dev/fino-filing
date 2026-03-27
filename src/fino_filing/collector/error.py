from datetime import date

from fino_filing.core.error import FinoFilingException


# Collector Validation Error
class CollectorDateRangeValidationError(FinoFilingException, ValueError):
    """Edinet Date Range Validation Error"""

    def __init__(self, date_from: date, date_to: date):
        super().__init__(
            f"Date range validation error: date_from: {date_from}, date_to: {date_to}"
        )
        self.date_from = date_from
        self.date_to = date_to


class CollectorParseResponseValidationError(FinoFilingException, ValueError):
    """Collector Parse Response Validation Error"""

    def __init__(self, field: str):
        super().__init__(f"null is returned for expected field: {field}")
        self.field = field


# HTTP Request Error
class HttpRequestError(FinoFilingException):
    """Raised when HTTP request fails."""

    def __init__(self, url: str, error: Exception):
        super().__init__(f"HTTP request failed: {url}, error: {error}")
        self.url = url
        self.error = error


class HttpRateLimitError(FinoFilingException):
    """Raised when API rate limit is exceeded."""

    def __init__(self):
        super().__init__("API rate limit exceeded.")


class HttpAuthenticationError(FinoFilingException):
    """Raised when API authentication fails (missing User-Agent)."""

    def __init__(self):
        super().__init__(
            "API authentication failed. Please check your credentials is correctly set."
        )


class HttpNotFoundError(FinoFilingException):
    """Raised when requested resource is not found."""

    def __init__(self, url: str):
        super().__init__(
            f"Requested resource not found. Please check your request parameters and try again: {url}"
        )
        self.url = url
