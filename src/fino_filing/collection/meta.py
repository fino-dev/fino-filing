# collection/meta.py
from .field import Field


class ModelMeta(type):
    """
    Model Metaclass（フィールド自動収集）

    責務:
        - クラス定義時にFieldを収集
        - _fields属性に保存
        - Descriptor protocolを有効化

    Collectionには依存しない。
    """

    def __new__(mcs, name, bases, attrs):
        # Fieldを収集
        fields = {}

        for key, value in attrs.items():
            if isinstance(value, Field):
                # Field名が未設定なら自動設定
                if not value.name:
                    value.name = key
                fields[key] = value

        # 親クラスのFieldを継承
        for base in bases:
            if hasattr(base, "_fields"):
                fields.update(base._fields)

        # クラス作成
        cls = super().__new__(mcs, name, bases, attrs)

        # _fields属性を設定
        cls._fields = fields

        return cls
