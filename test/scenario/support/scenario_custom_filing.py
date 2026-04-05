"""Importable custom Filing for scenario tests (Catalog _filing_class resolution)."""

from __future__ import annotations

from typing import Annotated

from fino_filing.filing.field import Field
from fino_filing.filing.filing import Filing


class ScenarioDeskFiling(Filing):
    """
    Custom desk memo filing used only in scenario tests.

    Indexed fields support Field/Expr queries after index.
    """

    portfolio_code: Annotated[
        str,
        Field(indexed=True, description="Portfolio code"),
    ]
    desk_tag: Annotated[
        str,
        Field(indexed=True, description="Desk tag"),
    ]
