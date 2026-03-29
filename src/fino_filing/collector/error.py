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


class CollectorLimitValidationError(FinoFilingException, ValueError):
    """Collector Limit Validation Error"""

    def __init__(self, limit: int):
        super().__init__(
            f"Limit validation error: limit must be greater than 0: {limit}"
        )
        self.limit = limit


class CollectorNoContentError(FinoFilingException, ValueError):
    """Collector No Content Error"""

    def __init__(self, content_id: str):
        super().__init__(f"No content found for content of id: {content_id}")
        self.content_id = content_id


class CollectorParseResponseValidationError(FinoFilingException, ValueError):
    """Collector Parse Response Validation Error"""

    def __init__(self, cause: str):
        super().__init__(f"expected field is not validated: {cause}")
        self.field = cause


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
