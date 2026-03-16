from datetime import datetime
from typing import Annotated, ClassVar

from fino_filing.filing.field import Field
from fino_filing.filing.filing import Filing

from .filing_edger_queries import EDGARFilingQuery


class EDGARFiling(Filing):
    """EDGAR Filing Template"""

    source = "EDGAR"

    # EDGAR固有フィールド（任意）。.q の型は scripts/generate_filing_queries.py で生成。
    cik: Annotated[str, Field(description="CIK")]
    accession_number: Annotated[str, Field(description="Accession Number")]
    company_name: Annotated[str, Field(description="Company Name")]
    form_type: Annotated[str, Field(description="Form Type")]
    filing_date: Annotated[datetime, Field(description="Filing Date")]
    period_of_report: Annotated[datetime, Field(description="Period of Report")]
    sic_code: Annotated[str, Field(description="SIC Code")]
    state_of_incorporation: Annotated[str, Field(description="State of Incorporation")]
    fiscal_year_end: Annotated[str, Field(description="Fiscal Year End")]

    q: ClassVar[EDGARFilingQuery]
