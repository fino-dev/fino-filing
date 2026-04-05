import pytest

from fino_filing.collector.edgar._helper import (
    _filenames_from_sec_index_json,
)


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edgar
class TestEdgarHelpers:
    class TestIndexJsonAndHtm:
        def test_filenames_from_sec_index_json_single_item_object(self) -> None:
            """index.json の item が単一オブジェクトのときも列挙できる"""
            raw = {
                "directory": {
                    "item": {
                        "name": "a.htm",
                        "type": "text.gif",
                        "size": "1",
                    }
                }
            }
            assert _filenames_from_sec_index_json(raw) == ["a.htm"]
