from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any

from fino_filing.filing.meta import FilingMeta

from .field import Field

if TYPE_CHECKING:
    pass


class Filing(metaclass=FilingMeta):
    """
    Filing Document（スキーマレス）

    責務:
        - データ保持
        - フィールド定義
        - 拡張可能モデル提供

    Collectionに依存しない。

    Usage:
        # モデルベース（Annotated形式）。default値は = 値 で指定
        class EDINETFiling(Filing):
            filer_name: Annotated[str, Field("filer_name", description="提出者名")]
            revenue: Annotated[float, Field("revenue", description="売上")] = 0.0

        filing = Filing(content=b"...", id="...", source="custom")
        filing.revenue  # 未設定時は 0.0
    """

    # ========== Core Fields (Descriptor) ==========
    # Annotatedで定義: 型とFieldを一元化し、認知的齟齬を解消
    id: Annotated[str, Field("id", str, indexed=True, description="Filing ID")]
    source: Annotated[
        str, Field("source", str, indexed=True, description="Data source")
    ]
    checksum: Annotated[
        str, Field("checksum", str, indexed=True, description="SHA256 checksum")
    ]
    name: Annotated[str, Field("name", str, indexed=True, description="File name")]
    is_zip: Annotated[bool, Field("is_zip", bool, indexed=True, description="ZIP flag")]
    created_at: Annotated[
        datetime,
        Field("created_at", datetime, indexed=True, description="Created timestamp"),
    ]

    def __init__(self, *, content: bytes, **kwargs: Any) -> None:
        """
        Args:
            content: オプション。渡した場合checksumをここで計算して設定する（保持しない）。
            **kwargs: フィールド値（id, source, name 等）。
        """

        # データストア（フラット）
        self._data = {}

        # メタクラスで収集した _defaults を先に適用
        for key, value in getattr(self.__class__, "_defaults", {}).items():
            setattr(self, key, value)

        # kwargs から値を設定（descriptor経由）。kwargs が優先。
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _validate():
        

    def verify_checksum(self, content: bytes) -> bool:
        """
        Checksum検証

        Args:
            content: コンテンツ

        Returns:
            検証結果
        """
        actual = self.make_checksum(content)
        expected = self._data.get("checksum")

        return actual == expected

    def to_dict(self) -> dict[str, Any]:
        """
        辞書化（完全フラット）

        Returns:
            フィールド辞書
        """
        result = {}

        for key, value in self._data.items():
            # datetime → ISO文字列変換
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value

        return result

    @classmethod
    def from_dict(cls, data: dict, storage: Any = None) -> Filing:
        """
        辞書から復元

        Args:
            data: フィールド辞書
            storage: Storageインスタンス

        Returns:
            Filingインスタンス
        """
        # datetime復元
        data_copy = data.copy()

        if "created_at" in data_copy and isinstance(data_copy["created_at"], str):
            data_copy["created_at"] = datetime.fromisoformat(data_copy["created_at"])

        return cls(_storage=storage, **data_copy)

    @classmethod
    def get_indexed_fields(cls) -> list[str]:
        """
        物理カラム化されるフィールド一覧

        Returns:
            フィールド名リスト
        """
        return [field.name for field in cls._fields.values() if field.indexed]

    def __repr__(self):
        id_ = self._data.get("id", "???")
        source = self._data.get("source", "???")
        return f"{self.__class__.__name__}(id={id_!r}, source={source!r})"


# ========== Template Models ==========


class EDINETFiling(Filing):
    """EDINET Filing Template"""

    # EDINET固有フィールド（任意）
    edinet_code: Annotated[str, Field("edinet_code", str, description="EDINETコード")]
    sec_code: Annotated[str, Field("sec_code", str, description="証券コード")]
    jcn: Annotated[str, Field("jcn", str, description="法人番号")]
    filer_name: Annotated[str, Field("filer_name", str, description="提出者名")]
    ordinance_code: Annotated[
        str, Field("ordinance_code", str, description="府令コード")
    ]
    form_code: Annotated[str, Field("form_code", str, description="様式コード")]
    doc_description: Annotated[str, Field("doc_description", str, description="書類名")]
    period_start: Annotated[
        datetime, Field("period_start", datetime, description="期間開始")
    ]
    period_end: Annotated[
        datetime, Field("period_end", datetime, description="期間終了")
    ]
    submit_datetime: Annotated[
        datetime, Field("submit_datetime", datetime, description="提出日時")
    ]


class EDGARFiling(Filing):
    """EDGAR Filing Template"""

    # EDGAR固有フィールド（任意）
    cik: Annotated[str, Field("cik", str, description="CIK")]
    accession_number: Annotated[
        str, Field("accession_number", str, description="Accession Number")
    ]
    company_name: Annotated[str, Field("company_name", str, description="Company Name")]
    form_type: Annotated[str, Field("form_type", str, description="Form Type")]
    filing_date: Annotated[
        datetime, Field("filing_date", datetime, description="Filing Date")
    ]
    period_of_report: Annotated[
        datetime, Field("period_of_report", datetime, description="Period of Report")
    ]
    sic_code: Annotated[str, Field("sic_code", str, description="SIC Code")]
    state_of_incorporation: Annotated[
        str, Field("state_of_incorporation", str, description="State of Incorporation")
    ]
    fiscal_year_end: Annotated[
        str, Field("fiscal_year_end", str, description="Fiscal Year End")
    ]


# ========== ユーザー拡張例 ==========


class MyCustomFiling(EDINETFiling):
    """ユーザー定義Filing（拡張）"""

    # カスタムフィールド
    ticker: Annotated[
        str, Field("ticker", str, indexed=True, description="Ticker Symbol")
    ]
    revenue: Annotated[float, Field("revenue", float, description="Revenue")]
    industry: Annotated[str, Field("industry", str, description="Industry")]
    market_cap: Annotated[float, Field("market_cap", float, description="Market Cap")]
    analyst_rating: Annotated[
        str, Field("analyst_rating", str, description="Analyst Rating")
    ]
