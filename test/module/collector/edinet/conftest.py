from datetime import datetime

import pytest

from fino_filing import EdinetConfig, RawDocument


@pytest.fixture
def edinet_config() -> EdinetConfig:
    return EdinetConfig(api_key="test-api-key", timeout=5)


@pytest.fixture
def sample_edinet_raw_document() -> RawDocument:
    """EDINET 用のサンプル RawDocument（ネットワーク不要でパース・build_filing 検証用）"""
    content = b"%PDF-1.4 dummy edinet document"
    meta = {
        "doc_id": "S100ABCD1234567890",
        "edinet_code": "E12345",
        "sec_code": "12345",
        "jcn": "1234567890123",
        "filer_name": "株式会社テスト",
        "ordinance_code": "010",
        "form_code": "030000",
        "doc_type_code": "120",
        "doc_description": "有価証券報告書",
        "period_start": datetime(2023, 4, 1),
        "period_end": datetime(2024, 3, 31),
        "submit_datetime": datetime(2024, 6, 28, 10, 0, 0),
        "parent_doc_id": None,
    }
    return RawDocument(content=content, meta=meta)
