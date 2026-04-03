"""SEC Archives index.json 解決ヘルパーの単体テスト"""

import pytest

from fino_filing.collector.edger.archives._resolve import (
    directory_items_from_index_json,
    list_xbrl_bundle_file_names,
    pick_main_document_from_index,
)


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edger
class TestEdgerArchivesResolve:
    """Archives _resolve helpers Test"""

    class TestDirectoryItemsFromIndexJson:
        """directory_items_from_index_json Test"""

        def test_normalizes_list_item(self) -> None:
            """item が配列のときそのままリスト化する"""
            data = {"directory": {"item": [{"name": "a.htm"}, {"name": "b.xml"}]}}
            rows = directory_items_from_index_json(data)
            assert [r.get("name") for r in rows] == ["a.htm", "b.xml"]

        def test_wraps_single_dict_item(self) -> None:
            """item が単一 dict のとき1要素リストにする"""
            data = {"directory": {"item": {"name": "only.xml"}}}
            rows = directory_items_from_index_json(data)
            assert len(rows) == 1 and rows[0]["name"] == "only.xml"

        def test_empty_when_missing(self) -> None:
            """directory / item が無いとき空リスト"""
            assert directory_items_from_index_json({}) == []

    class TestListXbrlBundleFileNames:
        """list_xbrl_bundle_file_names Test"""

        def test_filters_and_sorts(self) -> None:
            """拡張子フィルタ・index.htm 除外・ソート"""
            items = [
                {"name": "z.xml"},
                {"name": "0000320193-23-000106-index.htm"},
                {"name": "a.htm"},
                {"name": "pic.png"},
            ]
            assert list_xbrl_bundle_file_names(items) == ["a.htm", "z.xml"]

    class TestPickMainDocumentFromIndex:
        """pick_main_document_from_index Test"""

        def test_prefers_form_hint_in_name(self) -> None:
            """フォーム種別がファイル名に含まれる htm を優先"""
            items = [
                {"name": "exhibit1.htm"},
                {"name": "corp-10k-2023.htm"},
            ]
            assert pick_main_document_from_index(items, "10-K") == "corp-10k-2023.htm"

        def test_falls_back_to_first_non_index_htm(self) -> None:
            """ヒントが無ければ最初の非 index htm"""
            items = [
                {"name": "0000320193-23-000106-index.htm"},
                {"name": "body.htm"},
            ]
            assert pick_main_document_from_index(items, "4") == "body.htm"
