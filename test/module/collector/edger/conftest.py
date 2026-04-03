from datetime import datetime
from typing import Any

import pytest

from fino_filing import RawDocument

_ENTITY_COMMON_STOCK_DESC = (
    "Indicate number of shares or other units outstanding of each of registrant's "
    "classes of capital or common stock or other ownership interests, if and as stated "
    "on cover of related periodic report. Where multiple classes or units exist define "
    "each class/interest by adding class of stock items such as Common Class A [Member], "
    "Common Class B [Member] or Partnership Interest [Member] onto the Instrument "
    "[Domain] of the Entity Listings, Instrument."
)


@pytest.fixture
def edger_submissions_response_apple() -> dict[str, Any]:
    """
    SEC Submissions API 相当（Apple Inc. 形状の代表例）。
    filings.recent の並列配列はそれぞれ5件まで。
    """
    return {
        "cik": "0000320193",
        "entityType": "operating",
        "sic": "3571",
        "sicDescription": "Electronic Computers",
        "ownerOrg": "06 Technology",
        "insiderTransactionForOwnerExists": 0,
        "insiderTransactionForIssuerExists": 1,
        "name": "Apple Inc.",
        "tickers": ["AAPL"],
        "exchanges": ["Nasdaq"],
        "ein": "942404110",
        "lei": None,
        "description": "",
        "website": "",
        "investorWebsite": "",
        "category": "Large accelerated filer",
        "fiscalYearEnd": "0926",
        "stateOfIncorporation": "CA",
        "stateOfIncorporationDescription": "CA",
        "addresses": {
            "mailing": {
                "street1": "ONE APPLE PARK WAY",
                "street2": None,
                "city": "CUPERTINO",
                "stateOrCountry": "CA",
                "zipCode": "95014",
                "stateOrCountryDescription": "CA",
                "isForeignLocation": 0,
                "foreignStateTerritory": None,
                "country": None,
                "countryCode": None,
            },
            "business": {
                "street1": "ONE APPLE PARK WAY",
                "street2": None,
                "city": "CUPERTINO",
                "stateOrCountry": "CA",
                "zipCode": "95014",
                "stateOrCountryDescription": "CA",
                "isForeignLocation": None,
                "foreignStateTerritory": None,
                "country": None,
                "countryCode": None,
            },
        },
        "phone": "(408) 996-1010",
        "flags": "",
        "formerNames": [
            {
                "name": "APPLE INC",
                "from": "2007-01-10T05:00:00.000Z",
                "to": "2019-08-05T04:00:00.000Z",
            },
            {
                "name": "APPLE COMPUTER INC",
                "from": "1994-01-26T05:00:00.000Z",
                "to": "2007-01-04T05:00:00.000Z",
            },
        ],
        "filings": {
            "recent": {
                "accessionNumber": [
                    "0000102909-26-000630",
                    "0001780525-26-000005",
                    "0001780525-26-000003",
                    "0001059235-26-000004",
                    "0001216519-26-000004",
                ],
                "filingDate": [
                    "2026-03-26",
                    "2026-03-17",
                    "2026-03-06",
                    "2026-02-26",
                    "2026-02-26",
                ],
                "reportDate": [
                    "",
                    "2026-03-15",
                    "2026-03-01",
                    "2026-02-24",
                    "2026-02-24",
                ],
                "acceptanceDateTime": [
                    "2026-03-26T19:43:19.000Z",
                    "2026-03-17T22:31:17.000Z",
                    "2026-03-06T23:30:51.000Z",
                    "2026-02-26T23:34:19.000Z",
                    "2026-02-26T23:33:49.000Z",
                ],
                "act": ["34", "", "", "", ""],
                "form": ["SCHEDULE 13G/A", "4", "3", "4", "4"],
                "fileNumber": ["005-33632", "", "", "", ""],
                "filmNumber": ["26797709", "", "", "", ""],
                "items": ["", "", "", "", ""],
                "core_type": ["SCHEDULE 13G/A", "4", "3", "4", "4"],
                "size": [7205, 9251, 490535, 5753, 5760],
                "isXBRL": [0, 0, 0, 0, 0],
                "isInlineXBRL": [0, 0, 0, 0, 0],
                "primaryDocument": [
                    "xslSCHEDULE_13G_X02/primary_doc.xml",
                    "xslF345X05/wk-form4_1773786674.xml",
                    "xslF345X02/wk-form3_1772839848.xml",
                    "xslF345X05/wk-form4_1772148856.xml",
                    "xslF345X05/wk-form4_1772148826.xml",
                ],
                "primaryDocDescription": ["", "FORM 4", "FORM 3", "FORM 4", "FORM 4"],
            }
        },
    }


@pytest.fixture
def edger_company_facts_response_apple() -> dict[str, Any]:
    """
    SEC Company Facts API 相当（Apple Inc. / dei 由来の代表例）。
    EntityCommonStockSharesOutstanding の shares は5件まで。
    """
    return {
        "cik": 320193,
        "entityName": "Apple Inc.",
        "facts": {
            "dei": {
                "EntityCommonStockSharesOutstanding": {
                    "label": "Entity Common Stock, Shares Outstanding",
                    "description": _ENTITY_COMMON_STOCK_DESC,
                    "units": {
                        "shares": [
                            {
                                "end": "2009-06-27",
                                "val": 895816758,
                                "accn": "0001193125-09-153165",
                                "fy": 2009,
                                "fp": "Q3",
                                "form": "10-Q",
                                "filed": "2009-07-22",
                                "frame": "CY2009Q2I",
                            },
                            {
                                "end": "2009-10-16",
                                "val": 900678473,
                                "accn": "0001193125-09-214859",
                                "fy": 2009,
                                "fp": "FY",
                                "form": "10-K",
                                "filed": "2009-10-27",
                            },
                            {
                                "end": "2009-10-16",
                                "val": 900678473,
                                "accn": "0001193125-10-012091",
                                "fy": 2009,
                                "fp": "FY",
                                "form": "10-K/A",
                                "filed": "2010-01-25",
                                "frame": "CY2009Q3I",
                            },
                            {
                                "end": "2010-01-15",
                                "val": 906794589,
                                "accn": "0001193125-10-012085",
                                "fy": 2010,
                                "fp": "Q1",
                                "form": "10-Q",
                                "filed": "2010-01-25",
                                "frame": "CY2009Q4I",
                            },
                            {
                                "end": "2010-04-09",
                                "val": 909938383,
                                "accn": "0001193125-10-088957",
                                "fy": 2010,
                                "fp": "Q2",
                                "form": "10-Q",
                                "filed": "2010-04-21",
                                "frame": "CY2010Q1I",
                            },
                        ]
                    },
                }
            }
        },
    }


@pytest.fixture
def sample_raw_document() -> RawDocument:
    """EDGAR 用のサンプル RawDocument（ネットワーク不要でパース・build_filing 検証用）"""
    content = b"<html><body>SEC filing index</body></html>"
    meta: dict[str, Any] = {
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
        "_origin": "archives",
    }
    return RawDocument(content=content, meta=meta)
