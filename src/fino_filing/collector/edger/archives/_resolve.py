from __future__ import annotations

from typing import Any


def directory_items_from_index_json(index_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize SEC ``-index.json`` ``directory.item`` into a list of dict rows."""
    directory = index_data.get("directory") or {}
    raw = directory.get("item")
    if raw is None:
        return []
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    return []


def list_xbrl_bundle_file_names(items: list[dict[str, Any]]) -> list[str]:
    """
    List file names under a filing that are likely needed for XBRL / inline XBRL tooling.

    Excludes the HTML directory index page. Sorted for stable iteration order.
    """
    suffixes = (".xml", ".htm", ".html", ".xhtml")
    names: list[str] = []
    for row in items:
        name = row.get("name")
        if not isinstance(name, str) or not name:
            continue
        lower = name.lower()
        if lower.endswith("-index.htm"):
            continue
        if lower.endswith(suffixes):
            names.append(name)
    return sorted(set(names))


def pick_main_document_from_index(
    items: list[dict[str, Any]], form_type: str
) -> str | None:
    """
    Choose a main filing body from ``-index.json`` rows when Submissions ``primaryDocument`` fails.

    Prefers a non-index HTML whose name hints at the form type, then any non-index HTML,
    then XML, then plain text.
    """
    names = [
        row["name"] for row in items if isinstance(row.get("name"), str) and row["name"]
    ]
    if not names:
        return None
    form_hint = form_type.lower()
    form_compact = form_hint.replace("-", "").replace("_", "")

    def is_non_index_htm(n: str) -> bool:
        lower = n.lower()
        return lower.endswith((".htm", ".html")) and not lower.endswith("-index.htm")

    def name_matches_form(n: str) -> bool:
        if not form_compact:
            return False
        compact = n.lower().replace("-", "").replace("_", "")
        return form_compact in compact

    for name in names:
        if is_non_index_htm(name) and (
            name_matches_form(name) or "filing" in name.lower()
        ):
            return name
    for name in names:
        if is_non_index_htm(name):
            return name
    for name in names:
        if name.lower().endswith(".xml"):
            return name
    for name in names:
        if name.lower().endswith(".txt"):
            return name
    return None
