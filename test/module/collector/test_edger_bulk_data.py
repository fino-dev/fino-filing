"""EdgerBulkData の parse_response / to_filing を検証する"""

import hashlib

from fino_filing import EDGARFiling
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edger import EdgerBulkData, EdgerConfig


class TestEdgerBulkData:
    """EdgerBulkData: パースと EDGARFiling 生成"""

    def test_parse_response_normalizes_meta(
        self, sample_raw_document: RawDocument, edger_config: EdgerConfig
    ) -> None:
        """parse_response が meta を EdgerSecApi と同様の Parsed に正規化する"""
        bulk = EdgerBulkData(edger_config)
        parsed = bulk.parse_response(sample_raw_document)
        assert parsed["cik"] == "0000320193"
        assert parsed["accession_number"] == "0000320193-23-000106"
        assert parsed["company_name"] == "Apple Inc."
        assert parsed["form_type"] == "10-K"

    def test_to_filing_produces_edgar_filing(
        self, sample_raw_document: RawDocument, edger_config: EdgerConfig
    ) -> None:
        """to_filing が Parsed と content から EDGARFiling を生成する"""
        bulk = EdgerBulkData(edger_config)
        parsed = bulk.parse_response(sample_raw_document)
        filing = bulk.to_filing(parsed, sample_raw_document.content)
        assert isinstance(filing, EDGARFiling)
        assert filing.source == "EDGAR"
        assert filing.checksum == hashlib.sha256(sample_raw_document.content).hexdigest()
