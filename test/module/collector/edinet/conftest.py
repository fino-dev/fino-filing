from datetime import datetime
from typing import Any

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


@pytest.fixture
def edinet_document_list_response_type1() -> dict[str, Any]:
    return {
        "metadata": {
            "title": "提出された書類を把握するためのAPI",
            "parameter": {"date": "2025-04-01", "type": "1"},
            "resultset": {"count": 270},
            "processDateTime": "2026-03-22 00:00",
            "status": "200",
            "message": "OK",
        }
    }


@pytest.fixture
def edinet_document_list_response_type2_no_items() -> dict[str, Any]:
    return {
        "metadata": {
            "title": "提出された書類を把握するためのAPI",
            "parameter": {"date": "2025-04-02", "type": "2"},
            "resultset": {"count": 0},
            "processDateTime": "2026-03-22 00:00",
            "status": "200",
            "message": "OK",
        },
        "results": [],
    }


@pytest.fixture
def edinet_document_list_response_type2_5_items() -> dict[str, Any]:
    return {
        "metadata": {
            "title": "提出された書類を把握するためのAPI",
            "parameter": {"date": "2025-04-02", "type": "2"},
            "resultset": {"count": 5},
            "processDateTime": "2026-03-22 00:00",
            "status": "200",
            "message": "OK",
        },
        "results": [
            {
                "seqNumber": 9,
                "docID": "S100VIZF",
                "edinetCode": "E06264",
                "secCode": None,
                "JCN": "6010001098507",
                "filerName": "ＪＰモルガン・アセット・マネジメント株式会社",
                "fundCode": "G04728",
                "ordinanceCode": "030",
                "formCode": "04A000",
                "docTypeCode": "030",
                "periodStart": None,
                "periodEnd": None,
                "submitDateTime": "2025-04-02 09:18",
                "docDescription": "有価証券届出書（内国投資信託受益証券）",
                "issuerEdinetCode": None,
                "subjectEdinetCode": None,
                "subsidiaryEdinetCode": None,
                "currentReportReason": None,
                "parentDocID": None,
                "opeDateTime": None,
                "withdrawalStatus": "0",
                "docInfoEditStatus": "0",
                "disclosureStatus": "0",
                "xbrlFlag": "1",
                "pdfFlag": "1",
                "attachDocFlag": "1",
                "englishDocFlag": "0",
                "csvFlag": "1",
                "legalStatus": "1",
            },
            {
                "seqNumber": 2,
                "docID": "S100VGVQ",
                "edinetCode": "E26704",
                "secCode": None,
                "JCN": "6010001141324",
                "filerName": "カレラアセットマネジメント株式会社",
                "fundCode": "G11582",
                "ordinanceCode": "030",
                "formCode": "995000",
                "docTypeCode": "180",
                "periodStart": None,
                "periodEnd": None,
                "submitDateTime": "2025-04-02 09:02",
                "docDescription": "臨時報告書（内国特定有価証券）",
                "issuerEdinetCode": None,
                "subjectEdinetCode": None,
                "subsidiaryEdinetCode": None,
                "currentReportReason": "第29条第2項第4号",
                "parentDocID": None,
                "opeDateTime": None,
                "withdrawalStatus": "0",
                "docInfoEditStatus": "0",
                "disclosureStatus": "0",
                "xbrlFlag": "1",
                "pdfFlag": "1",
                "attachDocFlag": "0",
                "englishDocFlag": "0",
                "csvFlag": "1",
                "legalStatus": "1",
            },
            {
                "seqNumber": 3,
                "docID": "S100VGVS",
                "edinetCode": "E26704",
                "secCode": None,
                "JCN": "6010001141324",
                "filerName": "カレラアセットマネジメント株式会社",
                "fundCode": "G13525",
                "ordinanceCode": "030",
                "formCode": "995000",
                "docTypeCode": "180",
                "periodStart": None,
                "periodEnd": None,
                "submitDateTime": "2025-04-02 09:02",
                "docDescription": "臨時報告書（内国特定有価証券）",
                "issuerEdinetCode": None,
                "subjectEdinetCode": None,
                "subsidiaryEdinetCode": None,
                "currentReportReason": "第29条第2項第4号",
                "parentDocID": None,
                "opeDateTime": None,
                "withdrawalStatus": "0",
                "docInfoEditStatus": "0",
                "disclosureStatus": "0",
                "xbrlFlag": "1",
                "pdfFlag": "1",
                "attachDocFlag": "0",
                "englishDocFlag": "0",
                "csvFlag": "1",
                "legalStatus": "1",
            },
            {
                "seqNumber": 4,
                "docID": "S100VHLR",
                "edinetCode": "E06433",
                "secCode": None,
                "JCN": "3010001034076",
                "filerName": "東京海上アセットマネジメント株式会社",
                "fundCode": "G12561",
                "ordinanceCode": "030",
                "formCode": "995000",
                "docTypeCode": "180",
                "periodStart": None,
                "periodEnd": None,
                "submitDateTime": "2025-04-02 09:03",
                "docDescription": "臨時報告書（内国特定有価証券）",
                "issuerEdinetCode": None,
                "subjectEdinetCode": None,
                "subsidiaryEdinetCode": None,
                "currentReportReason": "第29条第2項第4号",
                "parentDocID": None,
                "opeDateTime": None,
                "withdrawalStatus": "0",
                "docInfoEditStatus": "0",
                "disclosureStatus": "0",
                "xbrlFlag": "1",
                "pdfFlag": "1",
                "attachDocFlag": "0",
                "englishDocFlag": "0",
                "csvFlag": "1",
                "legalStatus": "1",
            },
            {
                "seqNumber": 5,
                "docID": "S100VINX",
                "edinetCode": "E10677",
                "secCode": None,
                "JCN": "9010001021473",
                "filerName": "アセットマネジメントＯｎｅ株式会社",
                "fundCode": "G11885",
                "ordinanceCode": "030",
                "formCode": "995000",
                "docTypeCode": "180",
                "periodStart": None,
                "periodEnd": None,
                "submitDateTime": "2025-04-02 09:03",
                "docDescription": "臨時報告書（内国特定有価証券）",
                "issuerEdinetCode": None,
                "subjectEdinetCode": None,
                "subsidiaryEdinetCode": None,
                "currentReportReason": "第29条第2項第4号",
                "parentDocID": None,
                "opeDateTime": None,
                "withdrawalStatus": "0",
                "docInfoEditStatus": "0",
                "disclosureStatus": "0",
                "xbrlFlag": "1",
                "pdfFlag": "1",
                "attachDocFlag": "0",
                "englishDocFlag": "0",
                "csvFlag": "1",
                "legalStatus": "1",
            },
        ],
    }
