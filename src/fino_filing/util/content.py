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


def find_zip(file_names: list[str]) -> str | None:
    """
    Find the zip file in the list of file names
    """
    for name in file_names:
        if name.endswith(".zip"):
            return name
    return None


def build_zip_bytes(entries: dict[str, bytes]) -> bytes:
    """Combine multiple files into a single ZIP file"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, data in entries.items():
            zf.writestr(path, data)
    return buf.getvalue()
