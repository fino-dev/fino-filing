from datetime import datetime
from enum import Enum
from typing import Annotated

import pytest

from fino_filing.filing.error import FilingValidationError
from fino_filing.filing.field import Field
from fino_filing.filing.filing import Filing


@pytest.fixture
def datetime_now() -> datetime:
    return datetime.now()


# ================ Additional Fields Filing ================


class AdditionalFieldsFiling(Filing):
    additional_field: Annotated[
        str, Field("additional_field", str, description="Additional Field")
    ]
    additional_field_2: Annotated[
        int, Field("additional_field_2", int, description="Additional Field 2")
    ]


class TestFiling_Initialize_AdditionalFields:
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


# ================ Additional Default Fields Filing ================


class SpecificIdEnum(Enum):
    SpecificIdString = "specific_id_string"


class SpecificIdStringEnum(str, Enum):
    SpecificIdString = "specific_id_string"


class AdditionalDefaultFieldsFiling(Filing):
    # 型なし default値を指定
    source = "extended_source"
    # 型あり default値を指定
    is_zip: Annotated[bool, Field("is_zip", bool, description="ZIP flag")] = False
    # ** strからenumへの変換はベースの構造が違うため弾かれる
    # name: Annotated[SpecificIdEnum, Field("name", SpecificIdEnum, description="Name")] = SpecificIdEnum.SpecificIdString
    # ** 親クラスの型定義と一致しないものは静的に弾く
    # name: Annotated[int, Field("name", int, description="Name as int")] = 123
    # ** ENUM でも親クラスの型定義と一致しないものは静的に弾く
    # name: Annotated[
    #     SpecificIdStringEnum, Field("name", SpecificIdStringEnum, description="Name")
    # ] = SpecificIdStringEnum.SpecificIdString
    # 修正: リテラル型やEnum型を正しく使用


class TestFiling_Initialize_DefaultFields:
    def test_filing_initialize_without_default_fields_success(
        self, datetime_now: datetime
    ) -> None:
        """default値が設定されている場合にはインスタンス化で指定せずにdefault値が設定されることを確認する"""
        additional_default_fields_filing = AdditionalDefaultFieldsFiling(
            id="test_id",
            checksum="test_checksum",
            name="test_name",
            created_at=datetime_now,
        )

        assert additional_default_fields_filing.source == "extended_source"
        assert not additional_default_fields_filing.is_zip

    def test_filing_initialize_with_default_fields_success_override(
        self, datetime_now: datetime
    ) -> None:
        """default値を上書きしてもエラーにならず、上書きできることを確認する"""
        additional_default_fields_filing = AdditionalDefaultFieldsFiling(
            id="test_id",
            source="override_source",
            checksum="test_checksum",
            is_zip=True,
            name="test_name",
            created_at=datetime_now,
        )

        assert additional_default_fields_filing.source == "override_source"
        assert additional_default_fields_filing.is_zip is True


# TODO immutable 設定
