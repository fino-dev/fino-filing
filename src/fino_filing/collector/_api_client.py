import json
import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


class ApiClient:
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

    @staticmethod
    def request_bytes(url: str, headers: dict[str, str], timeout: int) -> bytes:
        last_err: Exception | None = None
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except (HTTPError, URLError) as e:
             