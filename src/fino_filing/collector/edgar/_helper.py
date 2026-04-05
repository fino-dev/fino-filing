"""Edgar 用共有ヘルパー。Config/Client/Collector から利用する。"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, TypedDict

from fino_filing.collector.edgar.archive.constant import (
    EDGAR_SUBMISSIONS_RECENT_PROPERTIES,
)
from fino_filing.collector.error import CollectorParseResponseValidationError


def _accession_to_dir(accession: str) -> str:
    """accession_number to Archives directory name"""
    return accession.replace("-", "")


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

    Returns naive datetime in UTC (tzinfo stripped) for alignment with Catalog
    DuckDB TIMESTAMP columns and Filing serialization.
    """
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"

        parsed = datetime.fromisoformat(s)
        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except (ValueError, TypeError):
        return None


def _parse_edgar_flag(value: str | None) -> bool | None:
    """
    Parse EDGAR flag string to boolean.
    """
    if not value:
        return None
    return {"0": False, "1": True}.get(value)


def _infer_edgar_archive_format(
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


def _filenames_from_sec_index_json(raw_index_json: dict[str, Any]) -> list[str]:
    """Get filenames relative path from SEC index.json"""
    directory = raw_index_json.get("directory")
    if not isinstance(directory, dict):
        return []
    item = directory.get("item")
    if item is None:
        return []
    if isinstance(item, dict):
        items: list[Any] = [item]
    elif isinstance(item, list):
        items = item
    else:
        return []
    out: list[str] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        name = it.get("name")
        if isinstance(name, str) and name.strip():
            out.append(name.strip())
    return out


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
