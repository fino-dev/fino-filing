from datetime import datetime
from typing import Annotated

from fino_filing.util.edgar import pad_cik

from fino_filing.filing.field import Field
from fino_filing.filing.filing import Filing


class EDGARArchiveFiling(Filing):
    """
    EDGAR Archive Filing
    """

    source = "EDGAR"

    @staticmethod
    def build_default_name(cik: str, accession: str) -> str:
        return f"CIK{pad_cik(cik)}-{accession}-index.htm"

    edgar_resource_kind: Annotated[
        str, Field(indexed=True, description="EDGAR Resource Kind")
    ] = "archive-index"
    cik: Annotated[
        str, Field(indexed=True, identifier=True, required=True, description="CIK")
    ]
    accession_number: Annotated[
        str,
        Field(
            indexed=True, identifier=True, required=True, description="Accession Number"
        ),
    ]
    filer_name: Annotated[str, Field(description="Company Name")]
    form_type: Annotated[
        str, Field(description="Form Type")
    ]  # @see https://www.sec.gov/submit-filings/forms-index
    filing_date: Annotated[datetime, Field(description="Filing Date")]
    period_of_report: Annotated[datetime, Field(description="Period of Report")]
    sic_code: Annotated[str, Field(description="SIC Code")]
    state_of_incorporation: Annotated[str, Field(description="State of Incorporation")]
    fiscal_year_end: Annotated[str, Field(description="Fiscal Year End")]


class EDGARCompanyFactsFiling(Filing):
    """
    EDGAR Company Facts Filing
    """

    source = "EDGAR"
    format = "json"
    is_zip = False

    @staticmethod
    def build_default_name(cik: str) -> str:
        return f"CIK{pad_cik(cik)}-companyfacts.json"

    edgar_resource_kind: Annotated[
        str,
        Field(indexed=True, description="EDGAR Resource Kind"),
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


class EDGARBulkFiling(Filing):
    """
    EDGAR Bulk Filing
    """

    source = "EDGAR"
    format = "zip"
    is_zip = True

    @staticmethod
    def build_default_name(type: str) -> str:
        return f"bulk-{type}.zip"

    edgar_resource_kind: Annotated[
        str, Field(indexed=True, description="EDGAR Resource Kind")
    ] = "bulk"
    type: Annotated[
        str, Field(indexed=True, identifier=True, required=True, description="Type")
    ]
