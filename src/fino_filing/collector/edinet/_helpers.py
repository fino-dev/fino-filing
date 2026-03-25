"""Edinet 用共有ヘルパー。Collector から利用する。"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from fino_filing.collector.base import Parsed
from fino_filing.filing.filing_edinet import EDINETFiling


def _parse_edinet_datetime(s: str | None) -> datetime | None:
    """ISO 形式の日時文字列または None を datetime に変換する。"""
    if not s:
        return None
    try:
        # マイクロ秒付き / タイムゾーン付きにも対応するため [:26] で切り捨て
        return datetime.fromisoformat(s.replace("Z", "+00:00")[:26])
    except (ValueError, TypeError):
        return None


def _coerce_edinet_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return _parse_edinet_datetime(value)
    return None


def _edinet_meta_to_parsed(meta: dict[str, Any]) -> Parsed:
    """一覧 API の 1 件または同一形状の meta を EDINETFiling 用 Parsed に変換する。"""
    doc_id = meta.get("docID") or meta.get("doc_id") or ""
    return {
        "doc_id": doc_id,
        "edinet_code": meta.get("edinetCode") or meta.get("edinet_code") or "",
        "sec_code": meta.get("secCode") or meta.get("sec_code") or "",
        "jcn": meta.get("JCN") or meta.get("jcn") or "",
        "filer_name": meta.get("filerName") or meta.get("filer_name") or "",
        "ordinance_code": meta.get("ordinanceCode") or meta.get("ordinance_code") or "",
        "form_code": meta.get("formCode") or meta.get("form_code") or "",
        "doc_type_code": meta.get("docTypeCode") or meta.get("doc_type_code") or "",
        "doc_description": meta.get("docDescription")
        or meta.get("doc_description")
        or "",
        "period_start": _coerce_edinet_datetime(
            meta.get("periodStart") or meta.get("period_start")
        ),
        "period_end": _coerce_edinet_datetime(
            meta.get("periodEnd") or meta.get("period_end")
        ),
        "submit_datetime": _coerce_edinet_datetime(
            meta.get("submitDateTime") or meta.get("submit_datetime")
        ),
        "parent_doc_id": meta.get("parentDocID") or meta.get("parent_doc_id"),
    }


def _build_edinet_filing(parsed: Parsed, content: bytes, name: str) -> EDINETFiling:
    """Parsed と content から EDINETFiling を組み立てる。"""
    checksum = hashlib.sha256(content).hexdigest()
    return EDINETFiling(
        source="EDINET",
        name=name,
        checksum=checksum,
        format="pdf",
        is_zip=False,
        doc_id=parsed.get("doc_id", ""),
        edinet_code=parsed.get("edinet_code", ""),
        sec_code=parsed.get("sec_code", ""),
        jcn=parsed.get("jcn", ""),
        filer_name=parsed.get("filer_name", ""),
        ordinance_code=parsed.get("ordinance_code", ""),
        form_code=parsed.get("form_code", ""),
        doc_type_code=parsed.get("doc_type_code", ""),
        doc_description=parsed.get("doc_description", ""),
        period_start=parsed.get("period_start"),
        period_end=parsed.get("period_end"),
        submit_datetime=parsed.get("submit_datetime"),
        parent_doc_id=parsed.get("parent_doc_id"),
        created_at=datetime.now(),
    )
