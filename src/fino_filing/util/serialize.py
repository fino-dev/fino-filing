from datetime import datetime
from typing import Any


def serialize(value: Any) -> str:
    """
    値を文字列化するUtility関数
    - datetime は ISO 形式に変換
    """
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)
