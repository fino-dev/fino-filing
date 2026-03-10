"""EDINET API 用ユーザー設定。Collector のインスタンス化時に渡す。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EdinetConfig:
    """
    EDINET API 用ユーザー設定。

    api_key: EDINET API 利用のための API キー（Subscription-Key）。必須。
    timeout: HTTP タイムアウト（秒）。
    """

    api_key: str
    timeout: int = 30
