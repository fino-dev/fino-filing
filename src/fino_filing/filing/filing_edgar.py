from datetime import date, datetime
from typing import Annotated

from fino_filing.collector.edgar.documents.enum import EdgarDocumentsFetchMode
from fino_filing.filing.field import Field
from fino_filing.filing.filing import Filing
from fino_filing.util.edgar import pad_cik


class EdgarArchiveFiling(Filing):
    """
    Edgar Archive Filing
    """

    source = "EDGAR"

    @staticmethod
    def build_default_name(
        cik: str, accession: str, fetch_mode: EdgarDocumentsFetchMode, format: str
    ) -> str:
        suffix = (
            "primary" if fetch_mode == EdgarDocumentsFetchMode.PRIMARY_ONLY else "full"
        )

        return f"CIK{pad_cik(cik)}_{accession}_{suffix}_{format}"

    edgar_resource_kind: Annotated[
        str, Field(indexed=True, description="Edgar Resource Kind")
    ] = "archive"
    cik: Annotated[
        str, Field(indexed=True, identifier=True, required=True, description="CIK")
    ]
    accession_number: Annotated[
        str,
        Field(
            indexed=True, identifier=True, required=True, description="Accession Number"
        ),
    ]
    entity_type: Annotated[str, Field(description="Entity Type")]
    filer_name: Annotated[str, Field(description="Company Name")]
    sic: Annotated[str, Field(description="SIC Code")]
    sic_description: Annotated[str, Field(description="SIC Description")]
    filer_category: Annotated[str, Field(description="Filer Category")]
    state_of_incorporation: Annotated[str, Field(description="State of Incorporation")]
    fiscal_year_end: Annotated[str, Field(description="Fiscal Year End")]
    tickers_key: Annotated[
        str,
        Field(
            indexed=True,
            description="Pipe-delimited sorted tickers(e.g. AAPL|MSFT)",
        ),
    ]
    exchanges_key: Annotated[
        str,
        Field(
            indexed=True,
            description="Pipe-delimited sorted exchanges(e.g. Nasdaq|NYSE)",
        ),
    ]
    filing_date: Annotated[date, Field(description="Filing Date")]
    report_date: Annotated[date, Field(description="Report Date")]
    acceptance_date_time: Annotated[datetime, Field(description="Acceptance Date Time")]
    act: Annotated[str, Field(description="Act")]
    form: Annotated[str, Field(description="Form")]
    items: Annotated[list[str], Field(description="Items")]
    core_type: Annotated[str, Field(description="Core Type")]
    is_xbrl: Annotated[bool, Field(description="Is XBRL")]
    is_inline_xbrl: Annotated[bool, Field(description="Is Inline XBRL")]
    primary_document: Annotated[str, Field(description="Primary Document")]
    primary_doc_description: Annotated[
        str, Field(description="Primary Doc Description")
    ]


class EdgarCompanyFactsFiling(Filing):
    """
    Edgar Company Facts Filing
    """

    source = "EDGAR"
    format = "json"
    is_zip = False

    @staticmethod
    def build_default_name(cik: str) -> str:
        return f"CIK{pad_cik(cik)}-companyfacts.json"

    edgar_resource_kind: Annotated[
        str,
        Field(indexed=True, description="Edgar Resource Kind"),
    ] = "companyfacts"

    cik: Annotated[
        str, Field(indexed=True, identifier=True, required=True, description="CIK")
    ]
    entity_type: Annotated[str, Field(description="Entity Type")]
    filer_name: Annotated[str, Field(description="Company Name")]
    sic: Annotated[str, Field(description="SIC Code")]
    sic_description: Annotated[str, Field(description="SIC Description")]
    filer_category: Annotated[str, Field(description="Filer Category")]
    state_of_incorporation: Annotated[str, Field(description="State of Incorporation")]
    fiscal_year_end: Annotated[str, Field(description="Fiscal Year End")]
    tickers_key: Annotated[
        str,
        Field(
            indexed=True,
            description="Pipe-delimited sorted tickers(e.g. AAPL|MSFT)",
        ),
    ]
    exchanges_key: Annotated[
        str,
        Field(
            indexed=True,
            description="Pipe-delimited sorted exchanges(e.g. Nasdaq|NYSE)",
        ),
    ]


class EdgarBulkFiling(Filing):
    """
    Edgar Bulk Filing
    """

    source = "EDGAR"
    format = "zip"
    is_zip = True

    @staticmethod
    def build_default_name(type: str) -> str:
        return f"bulk-{type}.zip"

    edgar_resource_kind: Annotated[
        str, Field(indexed=True, description="Edgar Resource Kind")
    ] = "bulk"
    type: Annotated[
        str, Field(indexed=True, identifier=True, required=True, description="Type")
    ]
