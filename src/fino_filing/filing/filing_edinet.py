from datetime import date, datetime
from typing import Annotated

from fino_filing.filing.error import FilingRequiredError
from fino_filing.filing.field import Field

from .filing import Filing


class EDINETFiling(Filing):
    """
    EDINET Filing Template

    Fixed Field
    - source(Data Source) = "EDINET"

    Additional Fields
    - doc_id(書類管理番号): str
    - edinet_code(EDINETコード): str
    - sec_code(証券コード): str
    - jcn(法人番号): str
    - filer_name(提出者名): str
    - ordinance_code(府令コード): str
    - form_code(様式コード): str
    - doc_type_code(書類種別コード): str
    - doc_description(書類名): str
    - period_start(期間開始): datetime
    - period_end(期間終了): datetime
    - submit_datetime(提出日時): datetime

    Additional Fields (Optional)
    - parent_doc_id(親書類管理番号): str | None
    """

    source = "EDINET"

    @staticmethod
    def build_default_name(
        doc_id: str | None,
        doc_description: str | None,
        format: str | None,
        is_zip: bool,
    ) -> str:
        base_parts = [part for part in (doc_id, doc_description) if part]

        if not base_parts:
            raise FilingRequiredError("doc_id or doc_description are required")

        base = "_".join(base_parts)

        if is_zip:
            return f"{base}.zip"
        elif format:
            return f"{base}.{format}"
        return base

    # use doc_id as identifier field
    doc_id: Annotated[
        str,
        Field(
            indexed=True,
            identifier=True,
            required=True,
            description="Doc ID(書類管理番号)",
        ),
    ]
    edinet_code: Annotated[str, Field(description="EDINET CODE(EDINETコード)")]
    sec_code: Annotated[str, Field(description="SEC CODE(証券コード)")]
    jcn: Annotated[str, Field(description="JCN(法人番号)")]
    filer_name: Annotated[str, Field(description="Filer Name(提出者名)")]
    fund_code: Annotated[str, Field(description="Fund Code(ファンドコード)")]
    ordinance_code: Annotated[str, Field(description="Ordinance Code(府令コード)")]
    form_code: Annotated[str, Field(description="Form Code(様式コード)")]
    doc_type_code: Annotated[str, Field(description="Doc Type Code(書類種別コード)")]
    doc_description: Annotated[str, Field(description="Doc Description(書類名)")]
    period_start: Annotated[date, Field(description="Period Start(期間開始)")]
    period_end: Annotated[date, Field(description="Period End(期間終了)")]
    submit_datetime: Annotated[datetime, Field(description="Submit Datetime(提出日時)")]
    current_report_reason: Annotated[
        str, Field(description="Current Report Reason(臨報提出事由)")
    ]
    parent_doc_id: Annotated[
        str | None, Field(description="Parent Doc ID(親書類管理番号)")
    ] = None
