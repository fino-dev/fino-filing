from typing import Any

import pytest

from fino_filing import EdinetConfig, RawDocument


@pytest.fixture
def tmp_edinet_config() -> EdinetConfig:
    return EdinetConfig(api_key="test-api-key", timeout=5)


@pytest.fixture
def sample_edinet_raw_document() -> RawDocument:
    """EDINET 用のサンプル RawDocument（ネットワーク不要でパース・build_filing 検証用）"""
    content = b"%PDF-1.4 dummy edinet document"
    meta = {
        "doc_id": "S100ABCD1234567890",
        "document_download_type": 1,
        "edinetCode": "E12345",
        "secCode": "12345",
        "JCN": "1234567890123",
        "filerName": "株式会社テスト",
        "ordinanceCode": "010",
        "formCode": "030000",
        "docTypeCode": "120",
        "docDescription": "有価証券報告書",
        "periodStart": "2023-04-01",
        "periodEnd": "2024-03-31",
        "submitDateTime": "2024-06-28 10:00",
        "parentDocID": None,
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
