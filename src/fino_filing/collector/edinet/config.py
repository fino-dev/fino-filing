from dataclasses import dataclass

from fino_filing.collector._http_client import HttpClientConfig


@dataclass(kw_only=True)
class EdinetConfig(HttpClientConfig):
    """
    EDINET API Configuration
    * Inherits from HttpClientConfig

    Properties:
    - api_key: EDINET API Subscription-Key. Required.
    - **Inherited from HttpClientConfig**
    """

    api_key: str

    # apply settings of EDINET API limits
    # @see https://time2log.com/ja/edinet/edinet-api%E3%81%AE%E5%88%A9%E7%94%A8%E5%88%B6%E9%99%90%E3%81%A8%E5%AF%BE%E7%AD%96%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6/
    rate_limit_delay: float = 1.0
    retry_backoff_factor: float = 10.0
    max_retries: int = 2
