from typing import TYPE_CHECKING, Annotated, Any, get_args, get_origin, get_type_hints

from fino_filing.filing.field import Field

if TYPE_CHECKING:
    pass


class FilingMeta(type):
    """
    Model Metaclass（フィールド自動収集）

    責務:
        - クラス定義時に Annotated[T, Field(...)] から Field を抽出・注入
        - _fields / _defaults に保存
        - Descriptor protocol を有効化

    フィールド定義は Annotated のみ。default値はクラス属性の = 値 で指定する。
    Collectionには依存しない。
    """

    def __new__(
        mcs: type["FilingMeta"],
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
    ) -> type:
        # 1. attrsからField, default値を収集（明示的代入）
        fields: dict[str, Field] = {}
        defaults: dict[str, Any] = {}

        # 2. 親クラスのFieldとdefaultを継承
        for base in bases:
            if hasattr(base, "_fields"):
                fields.update(base._fields)
            if hasattr(base, "_defaults"):
                defaults.update(base._defaults)

        # 3. クラス作成（Field定義はAnnotatedのみとし、default値は = 値 で指定する）
        cls = super().__new__(mcs, name, bases, attrs)

        # 4. Annotated[T, Field(...), ...]からFieldとdefaul値を抽出
        try:
            # クラス属性の型ヒントを取得
            hints = get_type_hints(cls, include_extras=True)
        except Exception:
            hints = {}

        for attr_name, hint in hints.items():
            # 型定義がAnnotatedとなっているか判定し、そうではないものはスキップ
            if get_origin(hint) is not Annotated:
                continue

            for meta in get_args(hint)[1:]:
                # meta情報でFieldではないものはスキップ
                if not isinstance(meta, Field):
                    continue

                # （型アノテーションによるデフォルト値）のクラス属性に、デフォルト値が設定されている場合は、それをdefaultsに保存
                if hasattr(cls, attr_name):
                    current_value = getattr(cls, attr_name)
                    if not isinstance(current_value, Field):
                        defaults[attr_name] = current_value

                # すでにFieldが定義されている場合は、再設定しない
                if attr_name in fields:
                    break

                # Fieldのフィールド名が未設定の場合は、必須のためattr_nameを設定
                if not meta.name:
                    meta.name = attr_name

                # Annotated の第一引数（型）を Field に注入（Expr 生成・バリデーションで利用）
                meta.field_type = get_args(hint)[0]

                setattr(cls, attr_name, meta)
                fields[attr_name] = meta
                break

        setattr(cls, "_fields", fields)
        setattr(cls, "_defaults", defaults)

        return cls
