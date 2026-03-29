"""バイト列のチェックサム・ZIP 判定などの共通ユーティリティ。"""

from __future__ import annotations

import hashlib
import io
import zipfile


def sha256_checksum(content: bytes) -> str:
    """コンテンツの SHA256 16進ダイジェストを返す。"""
    return hashlib.sha256(content).hexdigest()


def is_zip_content(content: bytes) -> bool:
    """コンテンツが ZIP アーカイブかどうかを zipfile で判定する。"""
    return zipfile.is_zipfile(io.BytesIO(content))
