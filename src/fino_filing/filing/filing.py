from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any

from fino_filing.filing.error import FilingValidationError
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

        filing = Filing(id="...", source="custom")
        filing.revenue  # 未設定時は 0.0
    """

    # メタクラスで設定されるクラス変数の型アノテーション
    _fields: dict[str, Field]
    _defaults: dict[str, Any]

    # ========== Core Fields (Descriptor) ==========
    # Annotatedで定義: 型とFieldを一元化し、認知的齟齬を解消
    id: Annotated[
        str, Field("id", str, indexed=True, immutable=True, description="Filing ID")
    ]
    source: Annotated[
        str,
        Field("source", str, indexed=True, immutable=True, description="Data source"),
    ]
    checksum: Annotated[
        str,
        Field("checksum", str, indexed=True, description="SHA256 checksum"),
    ]
    name: Annotated[
        str, Field("name", str, indexed=True, immutable=True, description="File name")
    ]
    is_zip: Annotated[bool, Field("is_zip", bool, indexed=True, description="ZIP flag")]
    created_at: Annotated[
        datetime,
        Field(
            "created_at",
            datetime,
            indexed=True,
            immutable=True,
            description="Created timestamp",
        ),
    ]

    def __init__(self, **kwargs: Any) -> None:
        """
        Args:
            **kwargs: フィールド値（id, source, name 等）。
        """

        # データストア（フラット）
        self._data: dict[str, Any] = {}

        # メタクラスで収集した _defaults を先に適用
        for key, value in getattr(self.__class__, "_defaults", {}).items():
            setattr(self, key, value)

        # kwargs から値を設定（descriptor経由で _data に格納）。defaults を上書き。immutable は上書き不可。
        for key, value in kwargs.items():
            setattr(self, key, value)

        # validation check
        self._validate()

    def _validate(self) -> None:
        """
        必須項目と型を検証する。required は _defaults に無いフィールド、型は Field._field_type を使用。
        """
        cls = self.__class__
        fields: dict[str, Any] = getattr(cls, "_fields", {})
        defaults: dict[str, Any] = getattr(cls, "_defaults", {})
        errors: list[str] = []
        error_fields: list[str] = []

        for attr_name, field in fields.items():
            data_value = self._data.get(attr_name)
            default_value = defaults.get(attr_name)

            is_required = attr_name not in defaults

            # if value is None or field._field_type is None:
            # continue

            # 必須フィールド（_defaultsに存在しないフィールド）に値が指定されていない場合にはエラー
            if is_required and (data_value is None):
                errors.append(f"{attr_name!r}: required field is missing or None")
                error_fields.append(attr_name)
                continue

            # 型チェック（_field_type が未注入の場合はスキップ）
            if field._field_type is None:
                continue

            if is_required:
                if not isinstance(data_value, field._field_type):
                    errors.append(
                        f"{attr_name!r}: expected {field._field_type!r}, got {type(data_value).__name__!r}"
                    )
                    error_fields.append(attr_name)
            else:
                if not isinstance(default_value, field._field_type):
                    errors.append(
                        f"{attr_name!r}: expected {field._field_type!r}, got {type(default_value).__name__!r}"
                    )
                    error_fields.append(attr_name)

        if errors:
            raise FilingValidationError(
                "Filing validation failed",
                errors=errors,
                fields=error_fields,
            )

    def to_dict(self) -> dict[str, Any]:
        """
        辞書化（完全フラット）

        Returns:
            フィールド辞書
        """
        result: dict[str, Any] = {}

        for key, value in self._data.items():
            # datetime → ISO文字列変換
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any], storage: Any = None) -> Filing:
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

    def __repr__(self) -> str:
        id_ = self._data.get("id", "???")
        source = self._data.get("source", "???")
        return f"{self.__class__.__name__}(id={id_!r}, source={source!r})"


# ========== Template Models ==========


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
