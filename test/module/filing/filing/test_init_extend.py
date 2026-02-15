from datetime import datetime
from typing import Annotated

import pytest

from fino_filing.filing.error import FilingValidationError
from fino_filing.filing.field import Field
from fino_filing.filing.filing import Filing

# ================ Extend Filing ================


class ExtendFiling(Filing):
    pass


class TestFiling_Initialize_ExtendFiling:
    """
    Filingを継承したFilingのインスタンス化をテストする。
    - 正常系: 継承したFilingにインスタンス化の際に値を設定した場合
    - 異常系: 継承したFilingにインスタンス化の際に値を設定しない場合
    - 異常系: 継承したFilingにインスタンス化の際に異なる型の値を設定した場合
    """

    def test_initialize_success(self, datetime_now: datetime) -> None:
        """値を設定した場合はエラーにならず、値が設定されることを確認する"""
        f = ExtendFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
        )
        assert f.id == "test_id"
        assert f.source == "test_source"
        assert f.checksum == "test_checksum"
        assert f.name == "test_name"
        assert f.is_zip is False
        assert f.created_at == datetime_now

    def test_initialize_with_lack_field_failed(self, datetime_now: datetime) -> None:
        """値を設定しない場合はエラーになることを確認する"""
        with pytest.raises(FilingValidationError) as fve:
            ExtendFiling(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
            )

        assert fve.value.fields == ["name", "is_zip", "created_at"]

    def test_initialize_with_invalid_field_failed(self, datetime_now: datetime) -> None:
        """異なる型の値を設定した場合はエラーになることを確認する"""
        with pytest.raises(FilingValidationError) as fve:
            ExtendFiling(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name=123,
                is_zip="test_is_zip",
                created_at=123,
            )
        assert fve.value.fields == ["name", "is_zip", "created_at"]


# ================ Additional Fields Filing ================


class AdditionalFieldsFiling(Filing):
    additional_field: Annotated[
        str, Field("additional_field", str, description="Additional Field")
    ]
    additional_field_2: Annotated[
        int, Field("additional_field_2", int, description="Additional Field 2")
    ]


class TestFiling_Initialize_AdditionalFields:
    """
    Filingにフィールドを追加した継承Filingのインスタンス化をテストする。
    - 正常系: 追加したフィールドにインスタンス化の際に値を設定した場合
    - 異常系: 追加したフィールドにインスタンス化の際に値を設定しない場合
    - 異常系: 追加したフィールドにインスタンス化の際に型が一致しない場合
    - 正常系: 追加したフィールドにインスタンス化の際に型を設定後、上書きを行う場合
    """

    def test_filing_initialize_additional_fields_success(
        self, datetime_now: datetime
    ) -> None:
        """インスタンス化の際に必須（default値が設定されていない）フィールドを指定した場合成功することを確認する"""
        additional_fields_filing = AdditionalFieldsFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
            additional_field="test_additional_field",
            additional_field_2=123,
        )

        assert additional_fields_filing.id == "test_id"
        assert additional_fields_filing.source == "test_source"
        assert additional_fields_filing.checksum == "test_checksum"
        assert additional_fields_filing.name == "test_name"
        assert additional_fields_filing.is_zip is False
        assert additional_fields_filing.created_at == datetime_now
        assert additional_fields_filing.additional_field == "test_additional_field"
        assert additional_fields_filing.additional_field_2 == 123

    def test_filing_initialize_additional_fields_with_lack_field(
        self, datetime_now: datetime
    ) -> None:
        """インスタンス化の際に必須（default値が設定されていない）フィールドを指定しない場合エラー"""
        with pytest.raises(FilingValidationError) as fve:
            AdditionalFieldsFiling(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                is_zip=False,
                created_at=datetime_now,
            )

        assert fve.value.fields == ["additional_field", "additional_field_2"]

        with pytest.raises(FilingValidationError) as fve:
            AdditionalFieldsFiling(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                is_zip=False,
                created_at=datetime_now,
                additional_field="test_additional_field",
            )

        assert fve.value.fields == ["additional_field_2"]

        with pytest.raises(FilingValidationError) as fve:
            AdditionalFieldsFiling(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                is_zip=False,
                created_at=datetime_now,
                additional_field_2=123,
            )

        assert fve.value.fields == ["additional_field"]

    def test_filing_initialize_additional_fields_with_invalid_field(
        self, datetime_now: datetime
    ) -> None:
        """型の不一致でエラー"""
        with pytest.raises(FilingValidationError) as fve:
            AdditionalFieldsFiling(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                is_zip=False,
                created_at=datetime_now,
                additional_field=False,
                additional_field_2=123.456,
            )

        assert fve.value.fields == ["additional_field", "additional_field_2"]

    def test_filing_initialize_additional_fields_override_success(
        self, datetime_now: datetime
    ) -> None:
        f = AdditionalFieldsFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
            additional_field="test_additional_field",
            additional_field_2=123,
        )

        f.additional_field = "overwrite_additional_field"
        f.additional_field_2 = 456

        assert f.additional_field == "overwrite_additional_field"
        assert f.additional_field_2 == 456


# ================ Additional Immutable Field Filing ================
class AdditionalImmutableFieldFiling(Filing):
    """immutable=True のフィールドを持つ Filing。上書き時に ValidationError を出す。"""

    unspecified_mutable_token: Annotated[
        str,
        Field(
            "unspecified_mutable_token", str, description="Unspecified mutable token"
        ),
    ]
    mutable_token: Annotated[
        str, Field("mutable_token", str, immutable=False, description="Mutable token")
    ]
    immutable_token: Annotated[
        str,
        Field("immutable_token", str, immutable=True, description="Immutable token"),
    ]


class TestFiling_Initialize_AdditionalImmutableFields:
    """
    FilingにFieldを追加した継承Filingのimmutableの振る舞いをテストする。
    - 正常系: 追加したフィールドにインスタンス化の際に値を設定した場合
    - 異常系: 追加したフィールドにインスタンス化の際に値を設定しない場合
    - 正常系: 追加したフィールドにインスタンス化の際に値を設定後、mutableなフィールドを上書き更新した場合 / 異常系: immutableフィールドを上書き更新した場合
    """

    def test_inititalize_success(self, datetime_now: datetime) -> None:
        """値を設定した場合はエラーにならず、値が設定されることを確認する"""
        f = AdditionalImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
            unspecified_mutable_token="test_unspecified_mutable_token",
            mutable_token="test_mutable_token",
            immutable_token="test_immutable_token",
        )
        assert f.unspecified_mutable_token == "test_unspecified_mutable_token"
        assert f.mutable_token == "test_mutable_token"
        assert f.immutable_token == "test_immutable_token"

    def test_initialize_with_lack_field_failed(self, datetime_now: datetime) -> None:
        """immutable で default ありのフィールドを渡さない場合は default が使われる"""
        with pytest.raises(FilingValidationError) as fve:
            f = AdditionalImmutableFieldFiling(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                is_zip=False,
                created_at=datetime_now,
            )

        assert fve.value.fields == [
            "unspecified_mutable_token",
            "mutable_token",
            "immutable_token",
        ]

    def test_immutable_field_override(self, datetime_now: datetime) -> None:
        """immutableなフィールドを上書きしようとするとエラー"""
        f = AdditionalImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
            unspecified_mutable_token="test_unspecified_mutable_token",
            mutable_token="test_mutable_token",
            immutable_token="test_immutable_token",
        )

        f.unspecified_mutable_token = "overwrite_unspecified_mutable_token"
        f.mutable_token = "overwrite_mutable_token"
        assert f.unspecified_mutable_token == "overwrite_unspecified_mutable_token"
        assert f.mutable_token == "overwrite_mutable_token"

        with pytest.raises(FilingValidationError) as exc_info:
            f.immutable_token = "overwrite"
        assert exc_info.value.fields == ["immutable_token"]


# ================ Additional Immutable Fields Filing With Default Values ================


class AdditionalDefaultImmutableFieldFiling(Filing):
    unspecified_mutable_token: Annotated[
        str,
        Field(
            "unspecified_mutable_token", str, description="Unspecified mutable token"
        ),
    ] = "default_unspecified_mutable_token"
    mutable_token: Annotated[
        str, Field("mutable_token", str, immutable=False, description="Mutable token")
    ] = "default_mutable_token"
    immutable_token: Annotated[
        str,
        Field("immutable_token", str, immutable=True, description="Immutable token"),
    ] = "default_immutable_token"


class TestFiling_Initialize_AdditionalDefaultImmutableFiling:
    """
    FilingにFieldを追加した継承Filingのdefault値の振る舞いをテストする。
    - 正常系: 追加したdefault値が設定されているフィールドにインスタンス化の際に値を設定しない場合
    - 正常系: 追加したmutableなdefault値が設定されているフィールドにインスタンス化の際に値を設定した場合
    - 異常系: 追加したimmutableなdefault値が設定されているフィールドにインスタンス化の際に値を設定した場合
    - 正常系: 追加したmutableなdefault値が設定されているフィールドにインスタンス化の際に値を設定せずに、上書きを行う場合
    - 正常系: 追加したmutableなdefault値が設定されているフィールドにインスタンス化の際に値を設定後、上書きを行う場合
    - 異常系: 追加したimmutableなdefault値が設定されているフィールドにインスタンス化の際に値を設定後、上書きを行う場合
    """

    def test_initialize_success(self, datetime_now: datetime) -> None:
        """default値を設定した場合はエラーにならず、default値が設定されることを確認する"""
        f = AdditionalDefaultImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
        )

        assert f.unspecified_mutable_token == "default_unspecified_mutable_token"
        assert f.mutable_token == "default_mutable_token"
        assert f.immutable_token == "default_immutable_token"

    def test_initialize_with_mutable_field_success(
        self, datetime_now: datetime
    ) -> None:
        """default値をMutableな値に設定した場合はエラーにならず、default値が設定されることを確認する"""
        f = AdditionalDefaultImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
            unspecified_mutable_token="test_unspecified_mutable_token",
            mutable_token="test_mutable_token",
        )

        assert f.unspecified_mutable_token == "test_unspecified_mutable_token"
        assert f.mutable_token == "test_mutable_token"
        assert f.immutable_token == "default_immutable_token"

    def test_initialize_with_immutable_field_failed(
        self, datetime_now: datetime
    ) -> None:
        """default値をImmutableな値に設定した場合はエラーになることを確認する"""
        with pytest.raises(FilingValidationError) as fve:
            AdditionalDefaultImmutableFieldFiling(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                is_zip=False,
                created_at=datetime_now,
                immutable_token="test_immutable_token",
            )

        assert fve.value.fields == ["immutable_token"]

    def test_override_mutable_after_initialize_without_value_success(
        self, datetime_now: datetime
    ) -> None:
        f = AdditionalDefaultImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
        )

        f.unspecified_mutable_token = "overwrite_unspecified_mutable_token"
        f.mutable_token = "overwrite_mutable_token"

        assert f.unspecified_mutable_token == "overwrite_unspecified_mutable_token"
        assert f.mutable_token == "overwrite_mutable_token"

    def test_override_mutable_after_initialize_with_value_success(
        self, datetime_now: datetime
    ) -> None:
        f = AdditionalDefaultImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
            unspecified_mutable_token="test_unspecified_mutable_token",
            mutable_token="test_mutable_token",
        )

        f.unspecified_mutable_token = "overwrite_unspecified_mutable_token"
        f.mutable_token = "overwrite_mutable_token"

        assert f.unspecified_mutable_token == "overwrite_unspecified_mutable_token"
        assert f.mutable_token == "overwrite_mutable_token"

    def test_override_immutable_after_initialize_without_value_failed(
        self, datetime_now: datetime
    ) -> None:
        f = AdditionalDefaultImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            created_at=datetime_now,
        )

        with pytest.raises(FilingValidationError) as fve:
            f.immutable_token = "overwrite_immutable_token"

        assert fve.value.fields == ["immutable_token"]


# ================ Override Existing Fields With Different Field Types Filing ================


class OverrideExistingFieldsWithDifferentFieldTypesFiling(Filing):
    # 異なる型定義をすると静的エラーになるが、pythonは実行可能のためテストする
    source: Annotated[int, Field("source", int, description="Source")] = 123  # type: ignore
    # 同じ型定義をする場合


# # class SpecificIdEnum(Enum):
# #     SpecificIdString = "specific_id_string"


# # class SpecificIdStringEnum(str, Enum):
# #     SpecificIdString = "specific_id_string"


# class AdditionalDefaultFieldsFiling(Filing):
#     # 型なし default値を指定
#     source = "extended_source"
#     # 型あり default値を指定
#     is_zip: Annotated[bool, Field("is_zip", bool, description="ZIP flag")] = False
#     # ** strからenumへの変換はベースの構造が違うため弾かれる
#     # name: Annotated[SpecificIdEnum, Field("name", SpecificIdEnum, description="Name")] = SpecificIdEnum.SpecificIdString
#     # ** 親クラスの型定義と一致しないものは静的に弾く
#     # name: Annotated[int, Field("name", int, description="Name as int")] = 123
#     # ** ENUM でも親クラスの型定義と一致しないものは静的に弾く
#     # name: Annotated[
#     #     SpecificIdStringEnum, Field("name", SpecificIdStringEnum, description="Name")
#     # ] = SpecificIdStringEnum.SpecificIdString
#     # 修正: リテラル型やEnum型を正しく使用


# class TestFiling_Initialize_DefaultFields:
#     """
#     Filingの既存Fieldにdefault値を設定した継承Filingのインスタンス化をテストする。
#     - 正常系: default値を設定しない場合
#     - 異常系: default値を設定（上書き）した場合
#     - 正常系: default値を動的に上書きした場合
#     """

#     def test_filing_initialize_without_default_fields_success(
#         self, datetime_now: datetime
#     ) -> None:
#         """default値が設定されている場合にはインスタンス化で指定せずにdefault値が設定されることを確認する"""
#         additional_default_fields_filing = AdditionalDefaultFieldsFiling(
#             id="test_id",
#             checksum="test_checksum",
#             name="test_name",
#             created_at=datetime_now,
#         )

#         assert additional_default_fields_filing.source == "extended_source"
#         assert not additional_default_fields_filing.is_zip

#     def test_filing_initialize_with_default_fields_success_override(
#         self, datetime_now: datetime
#     ) -> None:
#         """default値を上書きしてもエラーにならず、上書きできることを確認する"""
#         additional_default_fields_filing = AdditionalDefaultFieldsFiling(
#             id="test_id",
#             source="override_source",
#             checksum="test_checksum",
#             is_zip=True,
#             name="test_name",
#             created_at=datetime_now,
#         )

#         assert additional_default_fields_filing.source == "override_source"
#         assert additional_default_fields_filing.is_zip is True

#     def test_immutable_field_overwrite_after_init_success(
#         self, datetime_now: datetime
#     ) -> None:
#         """default値を初期化後に代入してもエラーにならず、代入できることを確�認する"""
#         f = AdditionalDefaultFieldsFiling(
#             id="test_id",
#             source="test_source",
#             checksum="test_checksum",
#             name="test_name",
#             created_at=datetime_now,
#         )
#         f.source = "override_source"
#         assert f.source == "override_source"
#         f.is_zip = True
#         assert f.is_zip is True


# # ================ Immutable Field Filing ================

# # class ImmutableFieldFiling(Filing):
