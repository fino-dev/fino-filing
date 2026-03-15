"""EdgerDocumentsCollector の collect フローと Collection 連携を検証する"""

from typing import Any, Iterator

import pytest

from fino_filing import EDGARFiling
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edger import EdgerConfig, EdgerDocumentsCollector


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edger
class TestEdgerDocumentsCollector:
    """EdgerDocumentsCollector: collect フローと add_to_collection"""

    def test_collect_adds_edgar_filing_to_collection(
        self,
        temp_collection: tuple,
        sample_raw_document: RawDocument,
        edger_config: EdgerConfig,
    ) -> None:
        """fetch_documents が 1 件返すとき collect() で 1 件が Collection に add される"""
        from fino_filing.collection.collection import Collection

        collection: Collection = temp_collection[0]

        class OneDocCollector(EdgerDocumentsCollector):
            def fetch_documents(self, **kwargs: Any) -> Iterator[RawDocument]:
                yield sample_raw_document

        collector = OneDocCollector(collection=collection, config=edger_config)
        results = collector.collect(cik_list=[])

        assert len(results) == 1
        filing, path = results[0]
        assert isinstance(filing, EDGARFiling)
        assert filing.source == "EDGAR"
        assert filing.accession_number == sample_raw_document.meta["accession_number"]
        assert path
        got = collection.get_filing(filing.id)
        assert got is not None
        assert got.accession_number == filing.accession_number
        content = collection.get_content(filing.id)
        assert content == sample_raw_document.content
