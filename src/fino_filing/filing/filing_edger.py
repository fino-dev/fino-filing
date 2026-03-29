from datetime import datetime
from typing import Annotated

from fino_filing.filing.field import Field
from fino_filing.filing.filing import Filing


class EDGARFiling(Filing):
    """
    EDGAR 提出書類1件（Submissions の filing 行＋Archives 実体）用テンプレート。

    Company Facts API や Bulk 全体 ZIP など、提出 accession と1対1にならないアーティファクトは
    EDGARCompanyFactsFiling 等の別サブクラスを使う。
    """

    source = "EDGAR"

    cik: Annotated[str, Field(description="CIK")]
    accession_number: Annotated[str, Field(description="Accession Number")]
    company_name: Annotated[str, Field(description="Company Name")]
    form_type: Annotated[str, Field(description="Form Type")]
    filing_date: Annotated[datetime, Field(description="Filing Date")]
    period_of_report: Annotated[datetime, Field(description="Period of Report")]
    sic_code: Annotated[str, Field(description="SIC Code")]
    state_of_incorporation: Annotated[str, Field(description="State of Incorporation")]
    fiscal_year_end: Annotated[str, Field(description="Fiscal Year End")]


class EDGARCompanyFactsFiling(Filing):
    """
    SEC Company Facts API（/api/xbrl/companyfacts/CIKxxx.json）のスナップショット1件用。

    Submissions 由来の会社メタのみ共有し、accession / form / 提出日は持たない。
    """

    source = "EDGAR"

    cik: Annotated[str, Field(description="CIK")]
    company_name: Annotated[str, Field(description="Company Name")]
    sic_code: Annotated[str, Field(description="SIC Code")]
    state_of_incorporation: Annotated[str, Field(description="State of Incorporation")]
    fiscal_year_end: Annotated[str, Field(description="Fiscal Year End")]
