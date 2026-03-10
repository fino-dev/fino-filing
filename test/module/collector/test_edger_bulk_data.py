"""EdgerBulkCollector の parse_response / build_filing を検証する"""

import hashlib

from fino_filing import EDGARFiling
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edger import EdgerBulkCollector, EdgerConfig
from fino_filing.collection.collection import Collection


class TestEdgerBulkCollector:
    """EdgerBulkCollector: パースと EDGARFiling 生成"""

    def test_parse_response_normalizes_meta(
        self, sample_raw_document: RawDocument, edger_config: EdgerConfig, temp_collection: tuple
    ) -> None:
        """parse_response が meta を Parsed に正規化する"""
        collection: Collection = temp_collection[0]
        bulk = EdgerBulkCollector(collection=collection, config=edger_config)
        parsed = bulk.parse_response(sample_raw_document)
        assert parsed["cik"] == "0000320193"
        assert parsed["accession_number"] == "0000320193-23-000106"
        assert parsed["company_name"] == "Apple Inc."
        assert parsed["form_type"] == "10-K"

    def test_build_filing_produces_edgar_filing(
        self, sample_raw_document: RawDocument, edger_config: EdgerConfig, temp_collection: tuple
    ) -> None:
        """build_filing が Parsed と content から EDGARFiling を生成する"""
        collection: Collection = temp_collection[0]
        bulk = EdgerBulkCollector(collection=collection, config=edger_config)
        parsed = bulk.parse_response(sample_raw_document)
        filing = bulk.build_filing(parsed, sample_raw_document)
        assert isinstance(filing, EDGARFiling)
        assert filing.source == "EDGAR"
        assert filing.checksum == hashlib.sha256(sample_raw_document.content).hexdigest()
