from typing import Any, TypedDict

from fino_filing.collector.edgar.documents.constants import (
    EDGAR_SUBMISSIONS_RECENT_PROPERTIES,
)
from fino_filing.collector.error import CollectorParseResponseValidationError


class EdgarSubmissionsRecentFilings(TypedDict):
    accessionNumber: list[str]
    filingDate: list[str]
    reportDate: list[str]
    acceptanceDateTime: list[str]
    act: list[str]
    form: list[str]
    items: list[str]
    core_type: list[str]
    isXBRL: list[bool]
    isInlineXBRL: list[bool]
    primaryDocument: list[str]
    primaryDocDescription: list[str]


def _verify_and_parse_edgar_submissions_recent_filings(
    cik: str,
    recent: dict[str, Any],
) -> EdgarSubmissionsRecentFilings:
    base_length = len(recent.get("accessionNumber", []))

    for property in EDGAR_SUBMISSIONS_RECENT_PROPERTIES:
        if property not in recent:
            raise CollectorParseResponseValidationError(
                f"CIK {cik} submissions.filings.recent: {property}"
            )

        if len(recent.get(property, [])) != base_length:
            raise CollectorParseResponseValidationError(
                f"CIK {cik} submissions.filings.recent length mismatch: {property}"
            )

    return {
        # 検証済みだが型エラー的に空配列をfallbackする
        "accessionNumber": recent.get("accessionNumber", []),
        "filingDate": recent.get("filingDate", []),
        "reportDate": recent.get("reportDate", []),
        "acceptanceDateTime": recent.get("acceptanceDateTime", []),
        "act": recent.get("act", []),
        "form": recent.get("form", []),
        "items": recent.get("items", []),
        "core_type": recent.get("core_type", []),
        "isXBRL": recent.get("isXBRL", []),
        "isInlineXBRL": recent.get("isInlineXBRL", []),
        "primaryDocument": recent.get("primaryDocument", []),
        "primaryDocDescription": recent.get("primaryDocDescription", []),
    }
