"""EDGAR 用ユーザー設定。Collector のインスタンス化時に渡す。"""

from __future__ import annotations

from dataclasses import dataclass

from fino_filing.collector._http_client import HttpClientConfig


@dataclass(kw_only=True)
class EdgarConfig(HttpClientConfig):
    """
    EDGAR 用ユーザー設定。

    user_agent_email: SEC が要求する連絡用メールアドレス（必須）。
        User-Agent ヘッダーは package 側で組み立てる。
    timeout: HTTP タイムアウト（秒）。
    """

    user_agent_email: str
