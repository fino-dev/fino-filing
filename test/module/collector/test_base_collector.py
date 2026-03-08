"""BaseCollector のテンプレートメソッド collect() のフローを検証する"""

import hashlib
from typing import Iterator

from fino_filing import Collection, Filing
from fino_filing.collector.base import BaseCollector, Parsed, RawDocument


class StubCollector(BaseCollector):
    """抽象メソッドをスタブ実装した具象クラス"""

    def __init__(self, collection: Collection) -> None:
        super().__init__(collection)
        self.fetch_called = 0
        self.parse_called = 0
        self.build_called = 0
        self.raws: list[RawDocument] = []

    def fetch_documents(self) -> Iterator[RawDocument]:
        self.fetch_called += 1
        yield from self.raws

    def parse_response(self, raw: RawDocument) -> Parsed:
        self.parse_called += 1
        return {"_raw_id": id(raw)}

    def build_filing(self, parsed: Parsed, raw: RawDocument) -> Filing:
        self.build_called += 1
        content = raw.content
        checksum = hashlib.sha256(content).hexdigest()
        return Filing(
            source="stub",
            checksum=checksum,
            name="stub.txt",
            is_zip=False,
            format="txt",
        )


class TestBaseCollector:
    """BaseCollector.collect() の呼び出し順と add の回数を検証する"""

    def test_collect_calls_fetch_then_parse_build_add_per_raw(
        self,
        temp_collection: tuple[Collection, object],
    ) -> None:
        """collect() が fetch_documents を1回呼び、各 raw に対して parse → build_filing → add_to_collection の順で呼ぶ"""
        collection, _ = temp_collection
        stub = StubCollector(collection)
        raw1 = RawDocument(content=b"a", meta={})
        raw2 = RawDocument(content=b"b", meta={})
        stub.raws = [raw1, raw2]

        results = stub.collect()

        assert stub.fetch_called == 1
        assert stub.parse_called == 2
        assert stub.build_called == 2
        assert len(results) == 2
        for (filing, path) in results:
            assert filing.source == "stub"
            assert path

    def test_collect_empty_list_adds_nothing(
        self,
        temp_collection: tuple[Collection, object],
    ) -> None:
        """fetch_documents が空リストのとき add は呼ばれない"""
        collection, _ = temp_collection
        stub = StubCollector(collection)
        stub.raws = []

        results = stub.collect()

        assert stub.fetch_called == 1
        assert stub.parse_called == 0
        assert stub.build_called == 0
        assert len(results) == 0
