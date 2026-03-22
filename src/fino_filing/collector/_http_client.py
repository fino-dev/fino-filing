import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from fino_filing.collector.error import (
    HttpAuthenticationError,
    HttpNotFoundError,
    HttpRateLimitError,
    HttpRequestError,
)

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class HttpClientConfig:
    """
    HttpClient configuration class

    Properties:
    - rate_limit_delay: Minimum delay between requests in seconds
    - retry_status_codes: Status codes to retry on
    - retry_methods: HTTP methods to retry on
    - retry_backoff_factor: Backoff factor for exponential backoff
    - max_retries: Maximum number of retry attempts
    - timeout: Request timeout in seconds
    """

    rate_limit_delay: float = 0.1
    retry_status_codes: list[int] = field(
        default_factory=lambda: [429, 500, 502, 503, 504]
    )
    retry_methods: list[str] = field(default_factory=lambda: ["GET"])
    retry_backoff_factor: float = 1.0
    max_retries: int = 3
    timeout: int = 30


class HttpClient:
    """
    HTTP client with rate limiting and error handling for SEC EDGAR API.

    This client handles:
    - Rate limiting to comply with 10 requests per second limit
    - Automatic retry logic for transient failures
    - Proper error handling and status code management
    - Required headers for API access

    Args:
        rate_limit_delay: Minimum delay between requests in seconds
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds

    Example:
        >>> client = HttpClient("MyApp/1.0 (contact@example.com)")
        >>> data = client.get("https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json")
    """

    def __init__(self, config: HttpClientConfig) -> None:
        self.rate_limit_delay = config.rate_limit_delay
        self.max_retries = config.max_retries
        self.timeout = config.timeout

        # Initialize last request time for rate limiting
        self._last_request_time = 0.0

        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=config.retry_backoff_factor,
            status_forcelist=config.retry_status_codes,
            allowed_methods=config.retry_methods,
        )

        # Register Adapter
        adopter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adopter)
        self.session.mount("https://", adopter)

        logger.info("HTTP client initialized")

    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        current_time = time.time()
        elapsed = current_time - self._last_request_time

        if elapsed < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.3f} seconds")
            time.sleep(sleep_time)

        self._last_request_time = time.time()

    def get(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Make HTTP GET request with rate limiting and error handling.

        Args:
            url: The URL to request
            params: Optional query parameters
            **kwargs: Additional arguments to pass to requests

        Returns:
            Parsed JSON response

        Raises:
            HttpRateLimitError: If rate limit is exceeded
            HttpAuthenticationError: If authentication fails (missing User-Agent).
            HttpNotFoundError: If resource is not found
            HttpRequestError: For other API errors
        """

        # 2回目以降はリクエスト間隔を指定時間だけ待つ（レート制限）
        self._rate_limit()

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
                **kwargs,
            )

            if response.status_code == 429:
                raise HttpRateLimitError()
            elif response.status_code == 401:
                raise HttpAuthenticationError()
            elif response.status_code == 404:
                raise HttpNotFoundError(url)

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            raise HttpRequestError(url, e) from e

    def get_raw(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> bytes:
        """
        Make HTTP GET request and return raw content.

        Args:
            url: The URL to request
            params: Optional query parameters
            **kwargs: Additional arguments to pass to requests

        Returns:
            Raw response content as bytes

        Raises:
            HttpRateLimitError: If rate limit is exceeded
            HttpAuthenticationError: If authentication fails (missing User-Agent).
            HttpNotFoundError: If resource is not found
            HttpRequestError: For other API errors
        """

        # 2回目以降はリクエスト間隔を指定時間だけ待つ（レート制限）
        self._rate_limit()

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
                **kwargs,
            )

            if response.status_code == 429:
                raise HttpRateLimitError()
            elif response.status_code == 401:
                raise HttpAuthenticationError()
            elif response.status_code == 404:
                raise HttpNotFoundError(url)

            response.raise_for_status()

            return response.content

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            raise HttpRequestError(url, e) from e

    @staticmethod
    def request_json(url: str, headers: dict[str, str], timeout: int) -> dict[str, Any]:
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=timeout) as resp:
                # responseのbyteをstrに変換してJSON としてパースする
                return json.loads(resp.read().decode())
        except (HTTPError, URLError, json.JSONDecodeError) as e:
            logger.error("Failed to fetch JSON and return empty dict %s: %s", url, e)
            return {}
