"""EdgerDocumentsCollector の parse_response / build_filing を検証する（ネットワーク不要）"""

import hashlib

import pytest

from fino_filing import EDGARFiling
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edger import EdgerConfig, EdgerDocumentsCollector
from fino_filing.collection.collection import Collection


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edger
class TestEdgerDocumentsCollectorParsing:
    """EdgerDocumentsCollector: パースと EDGARFiling 生成"""

    def test_parse_response_normalizes_meta(
        self,
        sample_raw_document: RawDocument,
        edger_config: EdgerConfig,
        temp_collection: tuple,
    ) -> None:
        """parse_response が meta を EDGARFiling 用の Parsed に正規化する"""
        collection: Collection = temp_collection[0]
        collector = EdgerDocumentsCollector(collection=collection, config=edger_config)
        parsed = collector.parse_response(sample_raw_document)
        assert parsed["cik"] == "0000320193"
        assert parsed["accession_number"] == "0000320193-23-000106"
        assert parsed["company_name"] == "Apple Inc."
        assert parsed["form_type"] == "10-K"
        assert parsed["sic_code"] == "3571"
        assert parsed["state_of_incorporation"] == "CA"
        assert parsed["fiscal_year_end"] == "09-30"
        assert parsed["primary_name"] == "0000320193-23-000106-index.htm"

    def test_build_filing_produces_edgar_filing(
        self,
        sample_raw_document: RawDocument,
        edger_config: EdgerConfig,
        temp_collection: tuple,
    ) -> None:
        """build_filing が Parsed と content から EDGARFiling を生成する"""
        collection: Collection = temp_collection[0]
        collector = EdgerDocumentsCollector(collection=collection, config=edger_config)
        parsed = collector.parse_response(sample_raw_document)
        filing = collector.build_filing(parsed, sample_raw_document)
        assert isinstance(filing, EDGARFiling)
        assert filing.source == "EDGAR"
        assert filing.cik == "0000320193"
        assert filing.accession_number == "0000320193-23-000106"
        assert filing.company_name == "Apple Inc."
        assert filing.form_type == "10-K"
        assert (
            filing.checksum == hashlib.sha256(sample_raw_document.content).hexdigest()
        )
