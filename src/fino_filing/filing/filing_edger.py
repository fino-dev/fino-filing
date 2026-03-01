from datetime import datetime
from typing import Annotated

from fino_filing import Field
from fino_filing.filing.filing import Filing


class EDGARFiling(Filing):
    """EDGAR Filing Template"""

    source = "EDGAR"

    # EDGAR固有フィールド（任意）
    cik: Annotated[str, Field(description="CIK")]
    accession_number: Annotated[str, Field(description="Accession Number")]
    company_name: Annotated[str, Field(description="Company Name")]
    form_type: Annotated[str, Field(description="Form Type")]
    filing_date: Annotated[datetime, Field(description="Filing Date")]
    period_of_report: Annotated[datetime, Field(description="Period of Report")]
    sic_code: Annotated[str, Field(description="SIC Code")]
    state_of_incorporation: Annotated[str, Field(description="State of Incorporation")]
    fiscal_year_end: Annotated[str, Field(description="Fiscal Year End")]
