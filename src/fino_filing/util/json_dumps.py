from __future__ import annotations

import json
from typing import Any


def json_dumps(obj: Any, /, **kwargs: Any) -> str:
    """
    Serialize obj to a JSON string, delegating to json.dumps.

    If the caller does not pass them, ensure_ascii is False and default is str
    so non-ASCII text stays readable and common non-JSON values serialize.
    Any keyword accepted by json.dumps may be passed and overrides these defaults.
    """
    kwargs.setdefault("ensure_ascii", False)
    kwargs.setdefault("default", str)
    return json.dumps(obj, **kwargs)
