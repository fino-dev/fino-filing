"""Edger 用共有ヘルパー。Config/Client/Collector から利用する。"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from fino_filing.collector.base import Parsed
from fino_filing.filing.filing_edger import EDGARFiling


def parse_edgar_date(s: str | None) -> datetime | None:
    """YYYY-MM-DD または None を datetime に変換する。"""
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def accession_to_dir(accession: str) -> str:
    """accession (0001104659-25-006631) を Archives ディレクトリ名 (000110465925006631) に変換する。"""
    return accession.replace("-", "")


def build_edgar_filing(parsed: Parsed, content: bytes, primary_name: str) -> EDGARFiling:
    """Parsed と content から EDGARFiling を組み立てる。3 Collector で共有する。"""
    checksum = hashlib.sha256(content).hexdigest()
    filing_date = parsed.get("filing_date")
    created_at = filing_date if isinstance(filing_date, datetime) else datetime.now()
    return EDGARFiling(
        source="EDGAR",
        name=primary_name,
        checksum=checksum,
        format=parsed.get("format", "htm"),
        is_zip=False,
        cik=parsed.get("cik", ""),
        accession_number=parsed.get("accession_number", ""),
        company_name=parsed.get("company_name", ""),
        form_type=parsed.get("form_type", ""),
        filing_date=parsed.get("filing_date") or created_at,
        period_of_report=parsed.get("period_of_report") or created_at,
        sic_code=parsed.get("sic_code", ""),
        state_of_incorporation=parsed.get("state_of_incorporation", ""),
        fiscal_year_end=parsed.get("fiscal_year_end", ""),
        created_at=created_at,
    )


def parse_meta_to_parsed(meta: dict[str, Any]) -> Parsed:
    """RawDocument.meta から EDGARFiling 用 Parsed を組み立てる。3 Collector で共有する。"""
    return {
        "cik": meta.get("cik", ""),
        "accession_number": meta.get("accession_number", ""),
        "company_name": meta.get("company_name", ""),
        "form_type": meta.get("form_type", ""),
        "filing_date": meta.get("filing_date"),
        "period_of_report": meta.get("period_of_report"),
        "sic_code": meta.get("sic_code", ""),
        "state_of_incorporation": meta.get("state_of_incorporation", ""),
        "fiscal_year_end": meta.get("fiscal_year_end", ""),
        "format": meta.get("format", "htm"),
        "primary_name": meta.get("primary_name", ""),
    }
