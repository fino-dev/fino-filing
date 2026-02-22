from datetime import datetime
from typing import Annotated

import pytest

from fino_filing.filing.error import (
    FieldImmutableError,
    FieldRequiredError,
    FilingValidationError,
)
from fino_filing.filing.field import Field
from fino_filing.filing.filing import Filing

# ================ Extend Filing ================


class ExtendFiling(Filing):
    pass


class TestExtendFiling_Initialize:
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
            format="xbrl",
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
        with pytest.raises(FieldRequiredError) as fve:
            ExtendFiling(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                format="xbrl",
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
                format="xbrl",
                created_at=123,
            )
        assert fve.value.fields == ["name", "is_zip", "created_at"]


# ================ Additional Fields Filing ================


class AdditionalFieldsFiling(Filing):
    additional_field: Annotated[str, Field(description="Additional Field")]
    additional_field_2: Annotated[int, Field(description="Additional Field 2")]


class TestExtendFiling_Initialize_AdditionalFields:
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
            format="xbrl",
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
        """required=False の追加フィールドは渡さなくても成功し、None になる"""
        f = AdditionalFieldsFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )
        assert f.additional_field is None
        assert f.additional_field_2 is None

        f2 = AdditionalFieldsFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
            additional_field="test_additional_field",
        )
        assert f2.additional_field == "test_additional_field"
        assert f2.additional_field_2 is None

        f3 = AdditionalFieldsFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
            additional_field_2=123,
        )
        assert f3.additional_field is None
        assert f3.additional_field_2 == 123

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
                format="xbrl",
                created_at=datetime_now,
                additional_field=False,
                additional_field_2=123.456,
            )

        assert fve.value.fields == ["additional_field", "additional_field_2"]

    def test_filing_initialize_additional_fields_overwrite_success(
        self, datetime_now: datetime
    ) -> None:
        f = AdditionalFieldsFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
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
        Field(description="Unspecified mutable token"),
    ]
    mutable_token: Annotated[str, Field(immutable=False, description="Mutable token")]
    immutable_token: Annotated[
        str,
        Field(immutable=True, description="Immutable token"),
    ]


class TestExtendFiling_Initialize_AdditionalImmutableFields:
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
            format="xbrl",
            created_at=datetime_now,
            unspecified_mutable_token="test_unspecified_mutable_token",
            mutable_token="test_mutable_token",
            immutable_token="test_immutable_token",
        )
        assert f.unspecified_mutable_token == "test_unspecified_mutable_token"
        assert f.mutable_token == "test_mutable_token"
        assert f.immutable_token == "test_immutable_token"

    def test_initialize_with_lack_field_failed(self, datetime_now: datetime) -> None:
        """required=False の追加フィールドは渡さなくても成功し、None になる"""
        f = AdditionalImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )
        assert f.unspecified_mutable_token is None
        assert f.mutable_token is None
        assert f.immutable_token is None

    def test_immutable_field_overwrite(self, datetime_now: datetime) -> None:
        """immutableなフィールドを上書きしようとするとエラー"""
        f = AdditionalImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
            unspecified_mutable_token="test_unspecified_mutable_token",
            mutable_token="test_mutable_token",
            immutable_token="test_immutable_token",
        )

        f.unspecified_mutable_token = "overwrite_unspecified_mutable_token"
        f.mutable_token = "overwrite_mutable_token"
        assert f.unspecified_mutable_token == "overwrite_unspecified_mutable_token"
        assert f.mutable_token == "overwrite_mutable_token"

        with pytest.raises(FieldImmutableError) as exc_info:
            f.immutable_token = "overwrite"
        assert exc_info.value.field == "immutable_token"


# ================ Additional Immutable Fields Filing With Default Values ================


class AdditionalDefaultImmutableFieldFiling(Filing):
    unspecified_mutable_token: Annotated[
        str,
        Field(description="Unspecified mutable token"),
    ] = "default_unspecified_mutable_token"
    mutable_token: Annotated[
        str, Field(immutable=False, description="Mutable token")
    ] = "default_mutable_token"
    immutable_token: Annotated[
        str,
        Field(immutable=True, description="Immutable token"),
    ] = "default_immutable_token"


class TestFiling_Initialize_AdditionalDefaultImmutableFiling:
    """
    FilingにFieldを追加した継承Filingのdefault値の振る舞いをテストする。
    - 正常系: 追加したdefault値が設定されているフィールドにインスタンス化の際に値を設定しない場合
    - 正常系: 追加したmutableなdefault値が設定されているフィールドにインスタンス化の際に値を設定した場合
    - 異常系: 追加したimmutableなdefault値が設定されているフィールドにインスタンス化の際に値を設定した場合
    - 正常系: 追加したmutableなdefault値が設定されているフィールドにインスタンス化の際に値を設定せずに、上書きを行う場合
    - 正常系: 追加したmutableなdefault値が設定されているフィールドにインスタンス化の際に値を設定後、上書きを行う場合
    - 異常系: 追加したimmutableなdefault値が設定されているフィールドにインスタンス化の際に値を設定せずインスタンス化後、上書きを行う場合
    """

    def test_initialize_success(self, datetime_now: datetime) -> None:
        """default値を設定した場合はエラーにならず、default値が設定されることを確認する"""
        f = AdditionalDefaultImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
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
            format="xbrl",
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
        with pytest.raises(FieldImmutableError) as fie_info:
            AdditionalDefaultImmutableFieldFiling(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                is_zip=False,
                format="xbrl",
                created_at=datetime_now,
                immutable_token="test_immutable_token",
            )

        assert fie_info.value.field == "immutable_token"

    def test_overwrite_mutable_after_initialize_without_value_success(
        self, datetime_now: datetime
    ) -> None:
        f = AdditionalDefaultImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )

        f.unspecified_mutable_token = "overwrite_unspecified_mutable_token"
        f.mutable_token = "overwrite_mutable_token"

        assert f.unspecified_mutable_token == "overwrite_unspecified_mutable_token"
        assert f.mutable_token == "overwrite_mutable_token"

    def test_overwrite_mutable_after_initialize_with_value_success(
        self, datetime_now: datetime
    ) -> None:
        f = AdditionalDefaultImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
            unspecified_mutable_token="test_unspecified_mutable_token",
            mutable_token="test_mutable_token",
        )

        f.unspecified_mutable_token = "overwrite_unspecified_mutable_token"
        f.mutable_token = "overwrite_mutable_token"

        assert f.unspecified_mutable_token == "overwrite_unspecified_mutable_token"
        assert f.mutable_token == "overwrite_mutable_token"

    def test_overwrite_immutable_after_initialize_without_value_failed(
        self, datetime_now: datetime
    ) -> None:
        f = AdditionalDefaultImmutableFieldFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )

        with pytest.raises(FieldImmutableError) as fve:
            f.immutable_token = "overwrite_immutable_token"

        assert fve.value.field == "immutable_token"


# ================ Existing Field With Default Value Extend Filing ================


class ExistingFieldDefaultFiling(Filing):
    # default値を持つフィールドとして上書きする
    checksum = "default_checksum"
    # # 異なるFieldの型で上書きする (型エラーを無視する)
    # is_zip = 123  # type: ignore


class TestExtendFiling_Initialize_ExistingFieldDefault:
    """
    既存FieldにDefault値を設定した継承FIlingのインスタンス化の振る舞いをテストする。
    - 正常系: 指定したDefault値が設定されることを確認する
    - 正常系: 指定したDefault値をインスタンス化の際に定義した場合、Default値が上書きされている場合
    - 正常系: 指定したDefault値をインスタンス化の際に指定せずその後、上書きを行う場合
    """

    def test_initialize_success(self, datetime_now: datetime) -> None:
        """指定したDefault値が設定されることを確認する"""
        f = ExistingFieldDefaultFiling(
            id="test_id",
            source="test_source",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )
        assert f.checksum == "default_checksum"

    def test_initialize_with_default_value_success(
        self, datetime_now: datetime
    ) -> None:
        """指定したDefault値のフィールドをインスタンス化の際に定義した場合、Default値が上書きされている"""
        f = ExistingFieldDefaultFiling(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )
        assert f.checksum == "test_checksum"

    def test_overwrite_after_initialize_success(self, datetime_now: datetime) -> None:
        """インスタンス化の際に指定せずその後、上書きを行う場合"""
        f = ExistingFieldDefaultFiling(
            id="test_id",
            source="test_source",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )
        f.checksum = "overwrite_checksum"
        assert f.checksum == "overwrite_checksum"


# ================ Existing Immutable Field With Default Value Extend Filing ================


class ExistingImmutableFieldDefaultFiling(Filing):
    # sourceはimmutableなフィールド
    source = "default_source"


class TestExtendFiling_Initialize_ExistingImmutableFieldDefault:
    """
    既存のImmutableなFieldにDefault値を設定した継承Filingのインスタンス化の振る舞いをテストする。
    - 正常系: 指定したDefault値が設定されることを確認する
    - 異常系: 指定したDefault値をインスタンス化の際に定義した場合
    - 異常系: 指定したDefault値をインスタンス化の際に指定せずその後、上書きを行う場合
    """

    def test_initialize_success(self, datetime_now: datetime) -> None:
        """指定したDefault値が設定されることを確認する"""
        f = ExistingImmutableFieldDefaultFiling(
            id="test_id",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )
        assert f.source == "default_source"

    def test_initialize_with_default_value_success(
        self, datetime_now: datetime
    ) -> None:
        """immutableなDefault値のフィールドをインスタンス化の際に定義した場合、エラー"""
        with pytest.raises(FieldImmutableError) as fve:
            ExistingImmutableFieldDefaultFiling(
                id="test_id",
                source="test_source",
                checksum="test_checksum",
                name="test_name",
                is_zip=False,
                format="xbrl",
                created_at=datetime_now,
            )
        assert fve.value.field == "source"

    def test_overwrite_after_initialize_success(self, datetime_now: datetime) -> None:
        """immutableなDefault値のフィールドをインスタンス化後、上書きしようとするとエラー"""
        f = ExistingImmutableFieldDefaultFiling(
            id="test_id",
            checksum="test_checksum",
            name="test_name",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )
        with pytest.raises(FieldImmutableError) as fve:
            f.source = "overwrite_source"
        assert fve.value.field == "source"


# ================ Required Field Default None Forbidden ================


class TestExtendFiling_RequiredFieldDefaultNoneForbidden:
    """
    Field(required=True) のフィールドに default None を設定することを禁止する仕様のテスト。
    Filing のコアフィールドは required=True で定義されている。
    ユーザーが独自フィールドに required=True を指定した場合も同様の挙動となる。
    - 異常系: required=True のフィールドに default None を設定したサブクラス定義時に FieldRequiredError が発生する
    - 異常系: required=True のフィールドに nullable な型と default None を設定したサブクラス定義時に FieldRequiredError が発生する
    - 正常系: required=True のフィールドに default を設定したサブクラス定義時に FieldRequiredError が発生しない
    - 正常系: ユーザー定義の Field(required=True) は default なしで定義し、インスタンス化時に値を渡すと成功する
    - 異常系: ユーザー定義の Field(required=True) に default None を設定した場合も FieldRequiredError が発生する
    - 異常系: ユーザー定義の Field(required=True) を渡さないと FieldRequiredError が発生する
    """

    def test_required_field_default_none_raises(self) -> None:
        """required=True のフィールドに default None を設定したサブクラス定義時に FieldRequiredError が発生する"""
        with pytest.raises(FieldRequiredError) as exc_info:

            class BadFiling(Filing):
                id = None  # type: ignore
                source = None  # type: ignore
                checksum = None  # type: ignore
                name = None  # type: ignore
                is_zip = None  # type: ignore
                created_at = None  # type: ignore

        assert exc_info.value.fields == [
            "id",
            "source",
            "checksum",
            "name",
            "is_zip",
            "created_at",
        ]
        assert len(exc_info.value.errors) == 6

    def test_required_field_default_none_raises_with_nullable_annotation(self) -> None:
        """required=True のフィールドに default None を設定したサブクラス定義時に FieldRequiredError が発生する"""
        with pytest.raises(FieldRequiredError) as exc_info:

            class BadFiling(Filing):
                id: Annotated[str | None, Field(required=True)] = None  # type: ignore
                source: Annotated[str | None, Field(required=True)] = None  # type: ignore
                checksum: Annotated[str | None, Field(required=True)] = None  # type: ignore
                name: Annotated[str | None, Field(required=True)] = None  # type: ignore
                is_zip: Annotated[bool | None, Field(required=True)] = None  # type: ignore
                created_at: Annotated[datetime | None, Field(required=True)] = None  # type: ignore

        assert exc_info.value.fields == [
            "id",
            "source",
            "checksum",
            "name",
            "is_zip",
            "created_at",
        ]
        assert len(exc_info.value.errors) == 6

    def test_user_defined_required_field_with_default_success(
        self, datetime_now: datetime
    ) -> None:
        """ユーザー定義の Field(required=True) は default なしで定義し、インスタンス化時に値を渡すと成功する"""

        class CustomDocFiling(Filing):
            doc_number: Annotated[
                str, Field(required=True, description="Document number")
            ] = "default_doc_number"

        f = CustomDocFiling(
            id="id1",
            source="src",
            checksum="csum",
            name="n",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )
        assert f.doc_number == "default_doc_number"

    def test_user_defined_required_field_without_default_success(
        self, datetime_now: datetime
    ) -> None:
        """ユーザー定義の Field(required=True) は default なしで定義し、インスタンス化時に値を渡すと成功する"""

        class CustomDocFiling(Filing):
            doc_number: Annotated[
                str, Field(required=True, description="Document number")
            ]

        f = CustomDocFiling(
            id="id1",
            source="src",
            checksum="csum",
            name="n",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
            doc_number="DOC-001",
        )
        assert f.doc_number == "DOC-001"

    def test_user_defined_required_field_default_none_raises(self) -> None:
        """ユーザー定義の Field(required=True) に default None を設定した場合も FieldRequiredError が発生する"""
        with pytest.raises(FieldRequiredError) as exc_info:

            class BadCustomFiling(Filing):
                doc_number: Annotated[
                    str, Field(required=True, description="Doc number")
                ] = None  # type: ignore

        assert exc_info.value.fields == ["doc_number"]

    def test_user_defined_required_field_missing_raises(
        self, datetime_now: datetime
    ) -> None:
        """ユーザー定義の Field(required=True) を渡さないと FieldRequiredError が発生する"""

        class CustomDocFiling(Filing):
            doc_number: Annotated[
                str, Field(required=True, description="Document number")
            ]

        with pytest.raises(FieldRequiredError) as exc_info:
            CustomDocFiling(
                id="id1",
                source="src",
                checksum="csum",
                name="n",
                is_zip=False,
                format="xbrl",
                created_at=datetime_now,
            )
        assert "doc_number" in exc_info.value.fields
