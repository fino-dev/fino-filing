from datetime import datetime

import pytest

from fino_filing import RawDocument


@pytest.fixture
def sample_raw_document() -> RawDocument:
    """EDGAR 用のサンプル RawDocument（ネットワーク不要でパース・build_filing 検証用）"""
    content = b"<html><body>SEC filing index</body></html>"
    meta = {
        "cik": "0000320193",
        "accession_number": "0000320193-23-000106",
        "filer_name": "Apple Inc.",
        "form_type": "10-K",
        "filing_date": datetime(2023, 10, 27),
        "period_of_report": datetime(2023, 9, 30),
        "sic_code": "3571",
        "state_of_incorporation": "CA",
        "fiscal_year_end": "09-30",
        "format": "htm",
        "primary_name": "0000320193-23-000106-index.htm",
        "_origin": "documents",
    }
    return RawDocument(content=content, meta=meta)
