from datetime import datetime
from typing import Annotated

from fino_filing.filing.field import Field

from .filing import Filing


class EDINETFiling(Filing):
    """
    EDINET Filing Template

    EDINET Fixed Field

    - source(Data Source) = "EDINET"

    EDINET Additional Fields

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

    EDINET Additional Fields (Optional)

    - parent_doc_id(親書類管理番号): str | None
    """

    # EDINET固定フィールド
    source = "EDINET"

    # EDINET 固有フィールド
    edinet_code: Annotated[
        str, Field("edinet_code", str, description="EDINET CODE(EDINETコード)")
    ]
    sec_code: Annotated[str, Field("sec_code", str, description="SEC CODE(証券コード)")]
    jcn: Annotated[str, Field("jcn", str, description="JCN(法人番号)")]
    filer_name: Annotated[
        str, Field("filer_name", str, description="Filer Name(提出者名)")
    ]
    ordinance_code: Annotated[
        str, Field("ordinance_code", str, description="Ordinance Code(府令コード)")
    ]
    form_code: Annotated[
        str, Field("form_code", str, description="Form Code(様式コード)")
    ]
    doc_type_code: Annotated[
        str, Field("doc_type_code", str, description="Doc Type Code(書類種別コード)")
    ]
    doc_description: Annotated[
        str, Field("doc_description", str, description="Doc Description(書類名)")
    ]
    period_start: Annotated[
        datetime, Field("period_start", datetime, description="Period Start(期間開始)")
    ]
    period_end: Annotated[
        datetime, Field("period_end", datetime, description="Period End(期間終了)")
    ]
    submit_datetime: Annotated[
        datetime,
        Field("submit_datetime", datetime, description="Submit Datetime(提出日時)"),
    ]
    parent_doc_id: Annotated[
        str | None,
        Field("parent_doc_id", str, description="Parent Doc ID(親書類管理番号)"),
    ] = None
