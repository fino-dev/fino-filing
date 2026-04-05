"""Edgar 用共有ヘルパー。Config/Client/Collector から利用する。"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fino_filing.collector.base import Parsed
from fino_filing.util.edgar import pad_cik


def _build_recent_submissions_json_file_name(cik: str) -> str:
    """Build submissions json name"""
    return f"CIK{pad_cik(cik)}-submissions.json"


def _build_company_facts_json_file_name(cik: str) -> str:
    """Build company facts json name"""
    return f"CIK{pad_cik(cik)}-companyfacts.json"


# TODO: Collector refactorで不要であれば消す。テストみ作成
def _parse_edgar_date(s: str | None) -> datetime | None:
    """YYYY-MM-DD または None を datetime に変換する。"""
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _accession_to_dir(accession: str) -> str:
    """accession_number to Archives directory name"""
    return accession.replace("-", "")


def _format_from_primary_filename(name: str) -> str:
    """Archives 上の相対パスからストレージ用 format（拡張子）を推定する。"""
    base = name.rsplit("/", 1)[-1]
    if "." in base:
        return base.rsplit(".", 1)[-1].lower()
    return "bin"


def _filenames_from_sec_index_json(raw: dict[str, Any]) -> list[str]:
    """Get filenames relative path from SEC index.json"""
    directory = raw.get("directory")
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


def _parse_meta_to_parsed(meta: dict[str, Any]) -> Parsed:
    """提出書類: RawDocument.meta から EdgarArchiveFiling 用 Parsed を組み立てる。"""
    return {
        "cik": meta.get("cik", ""),
        "accession_number": meta.get("accession_number", ""),
        "filer_name": meta.get("filer_name", ""),
        "form_type": meta.get("form_type", ""),
        "filing_date": meta.get("filing_date"),
        "period_of_report": meta.get("period_of_report"),
        "sic_code": meta.get("sic_code", ""),
        "state_of_incorporation": meta.get("state_of_incorporation", ""),
        "fiscal_year_end": meta.get("fiscal_year_end", ""),
        "format": meta.get("format", "htm"),
        "primary_name": meta.get("primary_name", ""),
        "is_zip": bool(meta.get("is_zip", False)),
    }
