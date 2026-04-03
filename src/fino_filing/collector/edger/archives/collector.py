from __future__ import annotations

import logging
from typing import Any, Iterator, Literal, cast, override

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Meta, Parsed, RawDocument
from fino_filing.collector.error import HttpNotFoundError
from fino_filing.filing.filing_edger import EDGARFiling

from .._helpers import (
    _build_edgar_filing,
    _parse_edgar_date,
    _parse_meta_to_parsed,
    pad_cik,
)
from ..client import EdgerClient
from ..config import EdgerConfig
from ._resolve import (
    directory_items_from_index_json,
    list_xbrl_bundle_file_names,
    pick_main_document_from_index,
)

logger = logging.getLogger(__name__)

EdgerArchivesFetchMode = Literal["filing_index", "primary", "xbrl_bundle"]


def _archives_file_format(file_name: str) -> str:
    lower = file_name.lower()
    if lower.endswith((".htm", ".html", ".xhtml")):
        return "htm"
    if lower.endswith(".xml"):
        return "xml"
    if lower.endswith(".txt"):
        return "txt"
    return "binary"


def _safe_archives_bytes(
    client: EdgerClient, cik_pad: str, accession: str, file_name: str
) -> bytes | None:
    try:
        data = client.get_archives_file(cik_pad, accession, file_name)
        return data if data else None
    except HttpNotFoundError:
        return None


class EdgerArchivesCollector(BaseCollector):
    """
    Collect filing artifacts from SEC Archives for EDGARFiling storage.

    Supports the filing HTML index page, Submissions ``primaryDocument`` with structured
    index fallback (for tools such as Arelle), and a filtered multi-file XBRL-oriented bundle.
    """

    def __init__(
        self,
        collection: Collection,
        config: EdgerConfig,
        *,
        fetch_mode: EdgerArchivesFetchMode = "primary",
    ) -> None:
        super().__init__(collection)
        self._client = EdgerClient(config)
        self._default_fetch_mode = fetch_mode

    @override
    def iter_collect(
        self,
        *,
        cik_list: list[str] | None = None,
        limit_per_company: int | None = None,
        fetch_mode: EdgerArchivesFetchMode | None = None,
        **kwargs: Any,
    ) -> Iterator[tuple[EDGARFiling, str]]:
        """Yields each saved ``(EDGARFiling, path)`` as documents are processed."""
        yield from cast(
            Iterator[tuple[EDGARFiling, str]],
            super().iter_collect(
                cik_list=cik_list,
                limit_per_company=limit_per_company,
                fetch_mode=fetch_mode,
                **kwargs,
            ),
        )

    @override
    def collect(
        self,
        *,
        cik_list: list[str] | None = None,
        limit_per_company: int | None = None,
        fetch_mode: EdgerArchivesFetchMode | None = None,
        **kwargs: Any,
    ) -> list[tuple[EDGARFiling, str]]:
        """Runs the collect flow and returns all resulting paths."""
        return list(
            self.iter_collect(
                cik_list=cik_list,
                limit_per_company=limit_per_company,
                fetch_mode=fetch_mode,
                **kwargs,
            )
        )

    @override
    def _fetch_documents(
        self,
        *,
        cik_list: list[str] | None = None,
        limit_per_company: int | None = None,
        fetch_mode: EdgerArchivesFetchMode | None = None,
        **kwargs: Any,
    ) -> Iterator[RawDocument]:
        mode = fetch_mode if fetch_mode is not None else self._default_fetch_mode
        if not cik_list:
            return
        for cik in cik_list:
            cik_pad = pad_cik(cik)
            submissions = self._client.get_submissions(cik)
            if not submissions:
                continue

            filer_name = submissions.get("name") or ""
            sic = (submissions.get("sic") or "").strip()
            sic_desc = submissions.get("sicDescription") or ""
            state = (submissions.get("stateOfIncorporation") or "").strip()
            fye = (submissions.get("fiscalYearEnd") or "").strip()

            filings_container = submissions.get("filings") or {}
            recent: dict[str, Any] = (
                filings_container.get("recent") or submissions.get("recent") or {}
            )
            accession_list: list[str] = recent.get("accessionNumber") or []
            form_list: list[str] = recent.get("form") or []
            filing_date_list: list[str] = recent.get("filingDate") or []
            report_date_list: list[str] = recent.get("reportDate") or []
            primary_doc_list: list[str] = recent.get("primaryDocument") or []

            n = min(
                len(accession_list),
                len(form_list),
                len(filing_date_list),
                len(report_date_list) if report_date_list else len(filing_date_list),
            )
            if limit_per_company is not None:
                n = min(n, limit_per_company)

            for i in range(n):
                accession = accession_list[i] if i < len(accession_list) else ""
                form = form_list[i] if i < len(form_list) else ""
                filing_date_s = filing_date_list[i] if i < len(filing_date_list) else ""
                report_date_s = (
                    report_date_list[i]
                    if report_date_list and i < len(report_date_list)
                    else filing_date_s
                )
                primary_hint = (
                    primary_doc_list[i]
                    if i < len(primary_doc_list) and primary_doc_list[i]
                    else ""
                )

                base_meta: dict[str, Any] = {
                    "cik": cik_pad,
                    "accession_number": accession,
                    "filer_name": filer_name,
                    "form_type": form,
                    "filing_date": _parse_edgar_date(filing_date_s),
                    "period_of_report": _parse_edgar_date(report_date_s),
                    "sic_code": sic or sic_desc,
                    "state_of_incorporation": state,
                    "fiscal_year_end": fye,
                    "_origin": "archives",
                    "archives_fetch_mode": mode,
                }

                if mode == "filing_index":
                    raw = self._raw_filing_index_row(cik_pad, accession, base_meta)
                    if raw:
                        yield raw
                elif mode == "primary":
                    raw = self._raw_primary_with_fallback(
                        cik_pad, accession, form, primary_hint, base_meta
                    )
                    if raw:
                        yield raw
                elif mode == "xbrl_bundle":
                    yield from self._iter_xbrl_bundle_rows(cik_pad, accession, base_meta)
                else:
                    logger.warning("Unknown archives fetch_mode %r; skipping", mode)

    def _raw_filing_index_row(
        self,
        cik_pad: str,
        accession: str,
        base_meta: dict[str, Any],
    ) -> RawDocument | None:
        file_name = f"{accession}-index.htm"
        content = _safe_archives_bytes(self._client, cik_pad, accession, file_name)
        if not content:
            return None
        meta = {
            **base_meta,
            "primary_name": file_name,
            "format": _archives_file_format(file_name),
        }
        return RawDocument(content=content, meta=meta)

    def _raw_primary_with_fallback(
        self,
        cik_pad: str,
        accession: str,
        form_type: str,
        primary_hint: str,
        base_meta: dict[str, Any],
    ) -> RawDocument | None:
        if primary_hint:
            content = _safe_archives_bytes(
                self._client, cik_pad, accession, primary_hint
            )
            if content:
                meta = {
                    **base_meta,
                    "primary_name": primary_hint,
                    "format": _archives_file_format(primary_hint),
                }
                return RawDocument(content=content, meta=meta)

        index_data = self._client.get_filing_index_json(cik_pad, accession)
        if index_data:
            items = directory_items_from_index_json(index_data)
            picked = pick_main_document_from_index(items, form_type)
            if picked:
                content = _safe_archives_bytes(
                    self._client, cik_pad, accession, picked
                )
                if content:
                    meta = {
                        **base_meta,
                        "primary_name": picked,
                        "format": _archives_file_format(picked),
                    }
                    return RawDocument(content=content, meta=meta)

        return self._raw_filing_index_row(cik_pad, accession, base_meta)

    def _iter_xbrl_bundle_rows(
        self,
        cik_pad: str,
        accession: str,
        base_meta: dict[str, Any],
    ) -> Iterator[RawDocument]:
        index_data = self._client.get_filing_index_json(cik_pad, accession)
        if not index_data:
            logger.debug(
                "No index.json for CIK %s accession %s; skipping bundle",
                cik_pad,
                accession,
            )
            return
        names = list_xbrl_bundle_file_names(
            directory_items_from_index_json(index_data)
        )
        if not names:
            logger.debug(
                "Empty XBRL bundle file list for CIK %s accession %s",
                cik_pad,
                accession,
            )
            return
        for file_name in names:
            content = _safe_archives_bytes(
                self._client, cik_pad, accession, file_name
            )
            if not content:
                continue
            meta = {
                **base_meta,
                "primary_name": file_name,
                "format": _archives_file_format(file_name),
            }
            yield RawDocument(content=content, meta=meta)

    @override
    def _parse_response(self, meta: Meta) -> Parsed:
        return _parse_meta_to_parsed(meta)

    @override
    def _build_filing(self, parsed: Parsed, content: bytes) -> EDGARFiling:
        primary_name = parsed.get("primary_name") or (
            parsed.get("accession_number", "") + "-index.htm"
        )
        return _build_edgar_filing(parsed, content, primary_name)


class EdgerDocumentsCollector(EdgerArchivesCollector):
    """
    Legacy entry point: same behavior as EdgerArchivesCollector with ``fetch_mode="filing_index"``.

    Prefer EdgerArchivesCollector and an explicit fetch mode for new code.
    """

    def __init__(
        self,
        collection: Collection,
        config: EdgerConfig,
        *,
        fetch_mode: EdgerArchivesFetchMode = "filing_index",
    ) -> None:
        super().__init__(collection, config, fetch_mode=fetch_mode)
