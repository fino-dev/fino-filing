# collection/models.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

# ========== Core Filing（基底） ==========


@dataclass
class CoreFiling(ABC):
    """Filing共通フィールド（最小限）"""

    # 不変ID
    filing_id: str
    source: str
    checksum: str

    # 共通メタデータ
    submit_date: datetime
    document_type: str

    # 内部管理用
    _storage: Optional[Any] = None
    _content_cache: Optional[bytes] = None

    # カスタムフィールド（動的拡張）
    custom_fields: dict[str, Any] = field(default_factory=dict)

    def get_content(self) -> bytes:
        """Payload取得（遅延ロード）"""
        if self._content_cache is None:
            if not self._storage:
                raise ValueError("Cannot load content: missing storage")
            self._content_cache = self._storage.load(self.filing_id)
        return self._content_cache

    def verify_checksum(self) -> bool:
        """Checksum検証"""
        import hashlib

        content = self.get_content()
        actual = hashlib.sha256(content).hexdigest()
        return actual == self.checksum

    @abstractmethod
    def to_dict(self) -> dict:
        """辞書化（サブクラスで拡張）"""
        ...

    @abstractmethod
    def get_searchable_fields(self) -> dict:
        """検索可能フィールド一覧"""
        ...


# ========== Source固有Filing ==========


@dataclass
class EdinetFiling(CoreFiling):
    # EDINET固有（型付き）
    edinet_code: Optional[str] = None  # 提出者EDINETコード
    sec_code: Optional[str] = None  # 証券コード
    jcn: Optional[str] = None  # 法人番号
    filer_name: Optional[str] = None  # 提出者名
    ordinance_code: Optional[str] = None  # 府令コード
    form_code: Optional[str] = None  # 様式コード
    doc_description: Optional[str] = None  # 書類名
    period_start: Optional[datetime] = None  # 期間（開始）
    period_end: Optional[datetime] = None  # 期間（終了）

    def __post_init__(self):
        self.source = "edinet"

    def to_dict(self) -> dict:
        """辞書化"""
        base = {
            "filing_id": self.filing_id,
            "source": self.source,
            "checksum": self.checksum,
            "submit_date": self.submit_date.isoformat(),
            "document_type": self.document_type,
        }

        # EDINET固有フィールド
        edinet_fields = {
            "edinet_code": self.edinet_code,
            "sec_code": self.sec_code,
            "jcn": self.jcn,
            "filer_name": self.filer_name,
            "ordinance_code": self.ordinance_code,
            "form_code": self.form_code,
            "doc_description": self.doc_description,
            "period_start": self.period_start.isoformat()
            if self.period_start
            else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
        }

        # カスタムフィールド
        return {**base, **edinet_fields, **self.custom_fields}

    def get_searchable_fields(self) -> dict:
        """検索可能フィールド定義"""
        return {
            # Core
            "filing_id": "TEXT",
            "source": "TEXT",
            "submit_date": "DATE",
            "document_type": "TEXT",
            # EDINET固有
            "edinet_code": "TEXT",
            "sec_code": "TEXT",
            "jcn": "TEXT",
            "filer_name": "TEXT",
            "ordinance_code": "TEXT",
            "form_code": "TEXT",
            "doc_description": "TEXT",
            "period_start": "DATE",
            "period_end": "DATE",
            # カスタム（動的に追加）
            **{k: self._infer_type(v) for k, v in self.custom_fields.items()},
        }

    def _infer_type(self, value: Any) -> str:
        """型推論"""
        if isinstance(value, (int, float)):
            return "REAL"
        elif isinstance(value, datetime):
            return "DATE"
        elif isinstance(value, bool):
            return "BOOLEAN"
        else:
            return "TEXT"

    @classmethod
    def from_dict(cls, data: dict, storage: Any = None) -> "EdinetFiling":
        """辞書からEdinetFiling復元"""
        return _edinet_from_dict(data, storage)


def _edinet_from_dict(data: dict, storage: Any = None) -> EdinetFiling:
    """EdinetFiling復元ヘルパー"""
    filing_data = data.copy()
    if isinstance(filing_data.get("submit_date"), str):
        filing_data["submit_date"] = datetime.fromisoformat(filing_data["submit_date"])
    for dt_field in ("period_start", "period_end"):
        val = filing_data.get(dt_field)
        if val and isinstance(val, str):
            filing_data[dt_field] = datetime.fromisoformat(val)

    core_fields = {
        "filing_id",
        "source",
        "checksum",
        "submit_date",
        "document_type",
        "edinet_code",
        "sec_code",
        "jcn",
        "filer_name",
        "ordinance_code",
        "form_code",
        "doc_description",
        "period_start",
        "period_end",
    }
    custom = {k: v for k, v in filing_data.items() if k not in core_fields}

    return EdinetFiling(
        filing_id=filing_data["filing_id"],
        source="edinet",
        checksum=filing_data["checksum"],
        submit_date=filing_data["submit_date"],
        document_type=filing_data["document_type"],
        edinet_code=filing_data.get("edinet_code"),
        sec_code=filing_data.get("sec_code"),
        jcn=filing_data.get("jcn"),
        filer_name=filing_data.get("filer_name"),
        ordinance_code=filing_data.get("ordinance_code"),
        form_code=filing_data.get("form_code"),
        doc_description=filing_data.get("doc_description"),
        period_start=filing_data.get("period_start"),
        period_end=filing_data.get("period_end"),
        _storage=storage,
        custom_fields=custom,
    )


@dataclass
class Filing(CoreFiling):
    """汎用Filing（Source固有でない）"""

    def to_dict(self) -> dict:
        """辞書化"""
        base = {
            "filing_id": self.filing_id,
            "source": self.source,
            "checksum": self.checksum,
            "submit_date": self.submit_date.isoformat(),
            "document_type": self.document_type,
        }
        return {**base, **self.custom_fields}

    def get_searchable_fields(self) -> dict:
        """検索可能フィールド定義"""
        return {
            "filing_id": "TEXT",
            "source": "TEXT",
            "submit_date": "DATE",
            "document_type": "TEXT",
            **{k: self._infer_type(v) for k, v in self.custom_fields.items()},
        }

    def _infer_type(self, value: Any) -> str:
        """型推論"""
        if isinstance(value, (int, float)):
            return "REAL"
        elif isinstance(value, datetime):
            return "DATE"
        elif isinstance(value, bool):
            return "BOOLEAN"
        else:
            return "TEXT"

    @classmethod
    def from_dict(cls, data: dict, storage: Any = None) -> "Filing":
        """辞書からFiling復元"""
        filing_data = data.copy()

        # submit_dateをdatetimeに変換
        if isinstance(filing_data.get("submit_date"), str):
            filing_data["submit_date"] = datetime.fromisoformat(
                filing_data["submit_date"]
            )

        # コアフィールド以外はcustom_fieldsへ
        core_fields = {
            "filing_id",
            "source",
            "checksum",
            "submit_date",
            "document_type",
        }
        custom = {k: v for k, v in filing_data.items() if k not in core_fields}

        return cls(
            filing_id=filing_data["filing_id"],
            source=filing_data["source"],
            checksum=filing_data["checksum"],
            submit_date=filing_data["submit_date"],
            document_type=filing_data["document_type"],
            _storage=storage,
            custom_fields=custom,
        )


@dataclass
class EdgarFiling(CoreFiling):
    # EDGAR固有（型付き）
    cik: Optional[str] = None  # Central Index Key
    accession_number: Optional[str] = None  # アクセション番号
    company_name: Optional[str] = None
    form_type: Optional[str] = None  # 10-K, 10-Q等
    filing_date: Optional[datetime] = None
    period_of_report: Optional[datetime] = None
    sic_code: Optional[str] = None  # Standard Industrial Classification
    state_of_incorporation: Optional[str] = None
    fiscal_year_end: Optional[str] = None

    def __post_init__(self):
        self.source = "edgar"

    def to_dict(self) -> dict:
        """辞書化"""
        base = {
            "filing_id": self.filing_id,
            "source": self.source,
            "checksum": self.checksum,
            "submit_date": self.submit_date.isoformat(),
            "document_type": self.document_type,
        }

        edgar_fields = {
            "cik": self.cik,
            "accession_number": self.accession_number,
            "company_name": self.company_name,
            "form_type": self.form_type,
            "filing_date": self.filing_date.isoformat() if self.filing_date else None,
            "period_of_report": self.period_of_report.isoformat()
            if self.period_of_report
            else None,
            "sic_code": self.sic_code,
            "state_of_incorporation": self.state_of_incorporation,
            "fiscal_year_end": self.fiscal_year_end,
        }

        return {**base, **edgar_fields, **self.custom_fields}

    def get_searchable_fields(self) -> dict:
        """検索可能フィールド定義"""
        return {
            # Core
            "filing_id": "TEXT",
            "source": "TEXT",
            "submit_date": "DATE",
            "document_type": "TEXT",
            # EDGAR固有
            "cik": "TEXT",
            "accession_number": "TEXT",
            "company_name": "TEXT",
            "form_type": "TEXT",
            "filing_date": "DATE",
            "period_of_report": "DATE",
            "sic_code": "TEXT",
            "state_of_incorporation": "TEXT",
            "fiscal_year_end": "TEXT",
            # カスタム
            **{k: self._infer_type(v) for k, v in self.custom_fields.items()},
        }

    def _infer_type(self, value: Any) -> str:
        if isinstance(value, (int, float)):
            return "REAL"
        elif isinstance(value, datetime):
            return "DATE"
        elif isinstance(value, bool):
            return "BOOLEAN"
        else:
            return "TEXT"

    @classmethod
    def from_dict(cls, data: dict, storage: Any = None) -> "EdgarFiling":
        """辞書からEdgarFiling復元"""
        return _edgar_from_dict(data, storage)


def _edgar_from_dict(data: dict, storage: Any = None) -> EdgarFiling:
    """EdgarFiling復元ヘルパー"""
    filing_data = data.copy()
    if isinstance(filing_data.get("submit_date"), str):
        filing_data["submit_date"] = datetime.fromisoformat(filing_data["submit_date"])
    for dt_field in ("filing_date", "period_of_report"):
        val = filing_data.get(dt_field)
        if val and isinstance(val, str):
            filing_data[dt_field] = datetime.fromisoformat(val)

    core_fields = {
        "filing_id",
        "source",
        "checksum",
        "submit_date",
        "document_type",
        "cik",
        "accession_number",
        "company_name",
        "form_type",
        "filing_date",
        "period_of_report",
        "sic_code",
        "state_of_incorporation",
        "fiscal_year_end",
    }
    custom = {k: v for k, v in filing_data.items() if k not in core_fields}

    return EdgarFiling(
        filing_id=filing_data["filing_id"],
        source="edgar",
        checksum=filing_data["checksum"],
        submit_date=filing_data["submit_date"],
        document_type=filing_data["document_type"],
        cik=filing_data.get("cik"),
        accession_number=filing_data.get("accession_number"),
        company_name=filing_data.get("company_name"),
        form_type=filing_data.get("form_type"),
        filing_date=filing_data.get("filing_date"),
        period_of_report=filing_data.get("period_of_report"),
        sic_code=filing_data.get("sic_code"),
        state_of_incorporation=filing_data.get("state_of_incorporation"),
        fiscal_year_end=filing_data.get("fiscal_year_end"),
        _storage=storage,
        custom_fields=custom,
    )


def filing_from_dict(data: dict, storage: Any = None) -> CoreFiling:
    """sourceに応じて適切なFilingクラスで復元"""
    source = data.get("source", "")
    if source == "edinet":
        return EdinetFiling.from_dict(data, storage)
    if source == "edgar":
        return EdgarFiling.from_dict(data, storage)
    return Filing.from_dict(data, storage)
