"""Edger 用共有ヘルパー。Config/Client/Collector から利用する。"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from fino_filing.collector.base import Parsed
from fino_filing.filing.filing_edger import EDGARCompanyFactsFiling, EDGARFiling
from fino_filing.util.delimited_symbols import normalize_delimited_multivalue


def _pad_cik(cik: str) -> str:
    """pad cik to 10 digits"""
    return cik.zfill(10)


def _parse_edgar_date(s: str | None) -> datetime | None:
    """YYYY-MM-DD または None を datetime に変換する。"""
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _accession_to_dir(accession: str) -> str:
    """accession (0001104659-25-006631) を Archives ディレクトリ名 (000110465925006631) に変換する。"""
    return accession.replace("-", "")


def _build_edgar_filing(
    parsed: Parsed, content: bytes, primary_name: str
) -> EDGARFiling:
    """提出書類用: Parsed と content から EDGARFiling を組み立てる。"""
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


def _build_edgar_company_facts_filing(
    parsed: Parsed, content: bytes, primary_name: str
) -> EDGARCompanyFactsFiling:
    """Company Facts JSON 用: Parsed と content から EDGARCompanyFactsFiling を組み立てる。"""
    checksum = hashlib.sha256(content).hexdigest()
    created_at = datetime.now()
    raw_tickers = parsed.get("tickers")
    raw_exchanges = parsed.get("exchanges")
    tickers_seq = raw_tickers if isinstance(raw_tickers, list) else []
    exchanges_seq = raw_exchanges if isinstance(raw_exchanges, list) else []
    tickers_strs = [str(x) for x in tickers_seq]
    exchanges_strs = [str(x) for x in exchanges_seq]
    return EDGARCompanyFactsFiling(
        source="EDGAR",
        name=primary_name,
        checksum=checksum,
        format=parsed.get("format", "json"),
        is_zip=False,
        cik=parsed.get("cik", ""),
        company_name=parsed.get("company_name", ""),
        sic=parsed.get("sic", ""),
        sic_description=parsed.get("sic_description", ""),
        filer_category=parsed.get("filer_category", ""),
        state_of_incorporation=parsed.get("state_of_incorporation", ""),
        fiscal_year_end=parsed.get("fiscal_year_end", ""),
        tickers_key=normalize_delimited_multivalue(tickers_strs),
        exchanges_key=normalize_delimited_multivalue(exchanges_strs),
        created_at=created_at,
    )


def _parse_meta_to_parsed(meta: dict[str, Any]) -> Parsed:
    """提出書類: RawDocument.meta から EDGARFiling 用 Parsed を組み立てる。"""
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


def _parse_company_facts_meta_to_parsed(meta: dict[str, Any]) -> Parsed:
    """Company Facts: RawDocument.meta から EDGARCompanyFactsFiling 用 Parsed を組み立てる。"""
    tickers = meta.get("tickers")
    exchanges = meta.get("exchanges")
    return {
        "cik": meta.get("cik", ""),
        "company_name": meta.get("company_name", ""),
        "sic": meta.get("sic") or meta.get("sic_code", ""),
        "sic_description": meta.get("sic_description", ""),
        "filer_category": meta.get("filer_category", ""),
        "state_of_incorporation": meta.get("state_of_incorporation", ""),
        "fiscal_year_end": meta.get("fiscal_year_end", ""),
        "format": meta.get("format", "json"),
        "primary_name": meta.get("primary_name", ""),
        "tickers": tickers if isinstance(tickers, list) else [],
        "exchanges": exchanges if isinstance(exchanges, list) else [],
    }
