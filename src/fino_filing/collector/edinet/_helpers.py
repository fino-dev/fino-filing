"""Edinet 用共有ヘルパー。Collector から利用する。"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from fino_filing.collector.base import Parsed
from fino_filing.filing.filing_edinet import EDINETFiling


def parse_edinet_datetime(s: str | None) -> datetime | None:
    """ISO 形式の日時文字列または None を datetime に変換する。"""
    if not s:
        return None
    try:
        # マイクロ秒付き / タイムゾーン付きにも対応するため [:26] で切り捨て
        return datetime.fromisoformat(s.replace("Z", "+00:00")[:26])
    except (ValueError, TypeError):
        return None


def list_item_to_parsed(item: dict[str, Any]) -> Parsed:
    """書類一覧 API の 1 件（results 要素）を EDINETFiling 用 Parsed に変換する。"""
    doc_id = item.get("docID") or item.get("doc_id") or ""
    return {
        "doc_id": doc_id,
        "edinet_code": item.get("edinetCode") or item.get("edinet_code") or "",
        "sec_code": item.get("secCode") or item.get("sec_code") or "",
        "jcn": item.get("JCN") or item.get("jcn") or "",
        "filer_name": item.get("filerName") or item.get("filer_name") or "",
        "ordinance_code": item.get("ordinanceCode") or item.get("ordinance_code") or "",
        "form_code": item.get("formCode") or item.get("form_code") or "",
        "doc_type_code": item.get("docTypeCode") or item.get("doc_type_code") or "",
        "doc_description": item.get("docDescription")
        or item.get("doc_description")
        or "",
        "period_start": parse_edinet_datetime(
            item.get("periodStart") or item.get("period_start")
        ),
        "period_end": parse_edinet_datetime(
            item.get("periodEnd") or item.get("period_end")
        ),
        "submit_datetime": parse_edinet_datetime(
            item.get("submitDateTime") or item.get("submit_datetime")
        ),
        "parent_doc_id": item.get("parentDocID") or item.get("parent_doc_id"),
    }


def meta_to_parsed(meta: dict[str, Any]) -> Parsed:
    """RawDocument.meta から EDINETFiling 用 Parsed を組み立てる。"""
    return {
        "doc_id": meta.get("doc_id", ""),
        "edinet_code": meta.get("edinet_code", ""),
        "sec_code": meta.get("sec_code", ""),
        "jcn": meta.get("jcn", ""),
        "filer_name": meta.get("filer_name", ""),
        "ordinance_code": meta.get("ordinance_code", ""),
        "form_code": meta.get("form_code", ""),
        "doc_type_code": meta.get("doc_type_code", ""),
        "doc_description": meta.get("doc_description", ""),
        "period_start": meta.get("period_start"),
        "period_end": meta.get("period_end"),
        "submit_datetime": meta.get("submit_datetime"),
        "parent_doc_id": meta.get("parent_doc_id"),
    }


def build_edinet_filing(parsed: Parsed, content: bytes, name: str) -> EDINETFiling:
    """Parsed と content から EDINETFiling を組み立てる。"""
    checksum = hashlib.sha256(content).hexdigest()
    submit_dt = parsed.get("submit_datetime")
    created_at = submit_dt if isinstance(submit_dt, datetime) else datetime.now()
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
        period_start=parsed.get("period_start") or created_at,
        period_end=parsed.get("period_end") or created_at,
        submit_datetime=parsed.get("submit_datetime") or created_at,
        parent_doc_id=parsed.get("parent_doc_id"),
        created_at=created_at,
    )
