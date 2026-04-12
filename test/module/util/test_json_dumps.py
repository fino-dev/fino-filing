"""fino_filing.util.json_dumps の単体テスト"""

from datetime import datetime

import pytest

from fino_filing import Filing, json_dumps as json_dumps_public
from fino_filing.util.json_dumps import json_dumps


@pytest.mark.module
class TestJsonDumps:
    """json_dumps Test"""

    class TestDefaults:
        def test_japanese_preserved_in_output(self) -> None:
            """デフォルトで ensure_ascii=False となり日本語がエスケープされないこと"""
            s = json_dumps({"提出者": "株式会社テスト", "note": "有価証券"})
            assert "株式会社テスト" in s
            assert "\\u682a" not in s

        def test_datetime_uses_default_str(self) -> None:
            """default=str 既定で datetime がシリアライズできること"""
            dt = datetime(2024, 1, 2, 3, 4, 5)
            s = json_dumps({"at": dt})
            assert "2024-01-02" in s

        def test_public_import_matches_util(self) -> None:
            """パッケージルートからの import が util と同一であること"""
            obj = {"a": 1}
            assert json_dumps_public(obj) == json_dumps(obj)

        def test_filing_to_dict_pretty_contains_japanese(self, datetime_now: datetime) -> None:
            """to_dict と json_dumps で日本語フィールドが読みやすい JSON になること"""
            filing = Filing(
                id="id1",
                source="src",
                checksum="ab" * 32,
                name="有価証券報告書_2024.xbrl",
                is_zip=False,
                format="xbrl",
                created_at=datetime_now,
            )
            text = json_dumps(filing.to_dict(), indent=2)
            assert "有価証券報告書" in text
            assert "\n" in text

    class TestJsonDumpsKwargs:
        def test_indent_pretty_print(self) -> None:
            """indent を渡すと整形されること"""
            s = json_dumps({"x": 1}, indent=2)
            assert "\n" in s

        def test_explicit_ensure_ascii_true_escapes_non_ascii(self) -> None:
            """ensure_ascii=True を明示すると非ASCIIがエスケープされること"""
            s = json_dumps({"k": "あ"}, ensure_ascii=True)
            assert "\\u" in s
            assert "あ" not in s

        def test_explicit_default_overrides(self) -> None:
            """default を明示すると既定の str が使われないこと"""

            def _default(_: object) -> str:
                return "custom"

            s = json_dumps({"x": datetime(2000, 1, 1)}, default=_default)
            assert "custom" in s
            assert "2000-01-01" not in s
