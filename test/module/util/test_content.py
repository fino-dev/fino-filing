"""fino_filing.util.content の単体テスト"""

import io
import zipfile

import pytest

from fino_filing.util.content import is_zip_content, sha256_checksum


@pytest.mark.module
class TestContentUtil:
    class TestSha256Checksum:
        def test_sha256_checksum_is_stable(self) -> None:
            data = b"hello"
            assert sha256_checksum(data) == sha256_checksum(b"hello")
            assert sha256_checksum(data) != sha256_checksum(b"world")

    class TestIsZipContent:
        def test_is_zip_content_true_for_zip_bytes(self) -> None:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as zf:
                zf.writestr("a.txt", b"x")
            assert is_zip_content(buf.getvalue()) is True

        def test_is_zip_content_false_for_pdf_magic(self) -> None:
            assert is_zip_content(b"%PDF-1.4\n") is False
