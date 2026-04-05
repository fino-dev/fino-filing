from datetime import date, datetime
from typing import Any, TypedDict

from fino_filing.collector.edgar.documents.constants import (
    EDGAR_SUBMISSIONS_RECENT_PROPERTIES,
)
from fino_filing.collector.error import CollectorParseResponseValidationError


def _parse_edgar_date(s: str | None) -> date | None:
    """
    EDGAR date string (YYYY-MM-DD) to date.
    If the string is not in the correct format, return None.
    """
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _parse_edgar_datetime(s: str | None) -> datetime | None:
    """
    EDGAR datetime string (ISO 8601, e.g. YYYY-MM-DDTHH:MM:SS.mmmZ) to datetime.
    """
    if not s:
        return None
    try:
        # Z (UTC) を ISO互換の +00:00 に変換
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"

        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _parse_edgar_flag(value: str | None) -> bool | None:
    """
    Parse EDGAR flag string to boolean.
    """
    if not value:
        return None
    return {"0": False, "1": True}.get(value)


def _infer_edgar_format(
    is_xbrl: bool | None, is_inline_xbrl: bool | None, primary_document: str | None
) -> str:
    """
    Infer EDGAR document format from flags and primary document.
    """
    if is_xbrl:
        return "xbrl"
    elif is_inline_xbrl:
        return "ixbrl"
    elif primary_document:
        primary_document_extension = primary_document.split(".")[-1]
        return primary_document_extension.lower()
    return "htm"


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
