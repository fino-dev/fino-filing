from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any, Self

from fino_filing.filing.error import (
    FieldValidationError,
    FilingRequiredError,
    FilingValidationError,
)
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
        # 必須にしたいフィールドは Field(required=True) で指定（コアと同様の挙動）
        class EDINETFiling(Filing):
            filer_name: Annotated[str, Field("filer_name", description="提出者名")]
            revenue: Annotated[float, Field("revenue", description="売上")] = 0.0

        filing = Filing(id="...", source="custom")
        filing.revenue  # 未設定時は 0.0
    """

    # メタクラスで設定されるクラス変数の型アノテーション
    _fields: dict[str, Field]
    _defaults: dict[str, Any]
    _data: dict[str, Any]

    # ========== Core Fields (Descriptor) ==========
    # required=True: Collection が前提とする必須項目。拡張時も Field(required=True) で同様の挙動を指定可能。
    _core_fields: list[str] = [
        "id",
        "source",
        "checksum",
        "name",
        "is_zip",
        "format",
        "created_at",
    ]
    id: Annotated[
        str,
        Field(indexed=True, immutable=True, required=True, description="Filing ID"),
    ]
    source: Annotated[
        str,
        Field(
            indexed=True,
            immutable=True,
            required=True,
            description="Data source",
        ),
    ]
    checksum: Annotated[
        str,
        Field(indexed=True, required=True, description="SHA256 checksum"),
    ]
    name: Annotated[
        str,
        Field(indexed=True, immutable=True, required=True, description="File name"),
    ]
    is_zip: Annotated[
        bool,
        Field(indexed=True, required=True, description="ZIP flag"),
    ]
    format: Annotated[
        str,
        Field(
            indexed=True,
            required=True,
            immutable=True,
            description="File format / extension for storage key (e.g. zip, xbrl, pdf, csv) => derived from is_zip.",
        ),
    ]
    created_at: Annotated[
        datetime,
        Field(
            indexed=True,
            immutable=True,
            required=True,
            description="Created timestamp",
        ),
    ]

    def __init__(self, **kwargs: Any) -> None:
        """
        Args:
            **kwargs: フィールド値（id, source, name 等）。
        """

        # データストア（フラット）を初期化（__setattr__をバイパス）
        object.__setattr__(self, "_data", {})

        # メタクラスで収集した _defaults を先に適用
        for key, value in getattr(self.__class__, "_defaults", {}).items():
            setattr(self, key, value)

        # kwargs から値を設定（descriptor経由で _data に格納）
        for key, value in kwargs.items():
            setattr(self, key, value)

        # validation check
        self.__validate_fields()

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Filingの属性代入時にimmutableチェックを行う

        Args:
            name: 属性名
            value: 設定する値
        """

        cls = self.__class__
        # Fieldとして定義されているかチェック
        if hasattr(cls, "_fields") and name in cls._fields:
            field = cls._fields[name]
            # immutableフィールドで既に値が設定されている場合はすでに値が存在している状態のためエラー（同一値の再設定は許可）
            if (
                field.immutable
                and name in self._data  # type: ignore[attr-defined]
                and self._data[name] != value  # type: ignore[attr-defined]
            ):
                from fino_filing.filing.error import FieldImmutableError

                raise FieldImmutableError(
                    f"Field {name!r} is immutable and cannot be overwritten",
                    field=name,
                    current_value=self._data[name],
                    attempt_value=value,
                )

        # 通常の属性設定（Fieldの場合はdescriptor経由で_dataに格納）
        object.__setattr__(self, name, value)

    def __validate_fields(self) -> None:
        """
        必須項目と型を検証する。
        required: Field.required が True のフィールドのみ必須。default の有無は判定に含めない。
        （required=False で default が無くても、インスタンス時に None のままであればエラーにしない）
        必須不足時は FilingRequiredError、型不一致時は FilingValidationError を送出する。
        """
        cls = self.__class__
        fields: dict[str, Any] = getattr(cls, "_fields", {})
        required_errors: list[str] = []
        required_fields: list[str] = []
        type_errors: list[str] = []
        type_fields: list[str] = []

        for attr_name, field in fields.items():
            data_value = self._data.get(attr_name)

            is_required = getattr(field, "required", False)

            # 必須フィールドに値が無い or None の場合
            if is_required and data_value is None:
                required_errors.append(
                    f"{attr_name!r}: required field is missing or None"
                )
                required_fields.append(attr_name)
                continue
            # filingのcore fieldは空文字を許容しない
            if attr_name in self._core_fields and data_value == "":
                type_errors.append(f"{attr_name!r}: core field cannot be empty")
                type_fields.append(attr_name)
                continue

            # 型チェック（_field_type が未注入の場合はスキップ）
            if field._field_type is None:
                continue
            # optional で値が None の場合は型チェックしない（None を許容）
            if not is_required and data_value is None:
                continue

            try:
                field.validate_value(data_value)
            except FieldValidationError as e:
                type_errors.append(e.message)
                type_fields.append(attr_name)

        if required_errors:
            raise FilingRequiredError(
                "Required field is missing or None",
                errors=required_errors,
                fields=required_fields,
            )
        if type_errors:
            raise FilingValidationError(
                "Filing validation failed",
                errors=type_errors,
                fields=type_fields,
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
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """
        辞書から復元

        Args:
            data: フィールド辞書

        Returns:
            呼び出し元クラスのインスタンス（Filing 継承時はそのサブクラス）
        """
        # datetime復元: すべてのdatetime型フィールドを自動変換
        data_copy = data.copy()
        fields: dict[str, Field] = getattr(cls, "_fields", {})

        for field_name, field in fields.items():
            if (
                field_name in data_copy
                and field._field_type is datetime
                and isinstance(data_copy[field_name], str)
            ):
                data_copy[field_name] = datetime.fromisoformat(data_copy[field_name])

        return cls(**data_copy)

    def get(self, key: str) -> Any:
        """
        フィールド値取得

        Args:
            key: フィールド名

        Returns:
            フィールド値
        """

        return self._data.get(key)

    @classmethod
    def get_indexed_fields(cls) -> list[str]:
        """
        物理カラム化されるフィールド一覧

        Returns:
            フィールド名リスト
        """
        return [field.name for field in cls._fields.values() if field.indexed]

    def __eq__(self, other: object) -> bool:
        """同一クラスかつ全フィールドが一致する場合に True"""
        if type(self) is not type(other):
            return False
        return self._data == getattr(other, "_data", None)

    def __repr__(self) -> str:
        all_fields = self._data.keys()
        all_fields_values = [self._data[field] for field in all_fields]
        all_fields_str = ", ".join(
            [f"{field}={value}" for field, value in zip(all_fields, all_fields_values)]
        )
        return f"{self.__class__.__name__}({all_fields_str})"
