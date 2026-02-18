from datetime import datetime
from typing import Annotated

import pytest

from fino_filing.filing.error import FilingImmutableError
from fino_filing.filing.field import Field
from fino_filing.filing.filing import Filing


class ImmutableDefaultFieldFiling(Filing):
    # mutableなフィールド
    checksum = "default_checksum"
    is_zip = False

    # immutable名なフィールド
    source = "default_source"
    name = "default_name"

    # additional field
    additional_field: Annotated[
        str, Field(immutable=True, description="Additional Field")
    ] = "default_additional_field"
    additional_field_2: Annotated[
        int, Field(immutable=True, description="Additional Field 2")
    ] = 123


class ImmutableDefaultFieldNoOverrideFiling(ImmutableDefaultFieldFiling):
    pass


class ImmutableDefaultFieldMutableOverrideFiling(ImmutableDefaultFieldFiling):
    checksum = "override_checksum"


class TestExtendFiling_Initialize_ImmutableDefaultFieldOverride:
    """
    ImmutableなDefault値を設定したFilingをさらに継承して上書きをした場合の振る舞いをテストする。
    - 正常系: 親クラスのdefault値が正常に設定されていること
    - 正常系: 親クラスのmutableなDefault値は全ての上書きを許容する
    - 異常系: 親クラスのimmutableなDefault値は子クラスのdefault値の設定を許容しない（複数）
    - 異常系: 親クラスのimmutableなDefault値は子クラスのインスタンス化の値の設定を許容しない
    - 異常系: 親クラスのimmutableなDefault値は子クラスでインスタンス化後の代入しようとしても許容しない
    """

    def test_initialize_success(self, datetime_now: datetime) -> None:
        f = ImmutableDefaultFieldNoOverrideFiling(
            id="test_id",
            created_at=datetime_now,
        )
        assert f.checksum == "default_checksum"
        assert f.is_zip is False
        assert f.source == "default_source"
        assert f.name == "default_name"
        assert f.additional_field == "default_additional_field"
        assert f.additional_field_2 == 123

    def test_initialize_with_mutable_default_value_override_success(
        self, datetime_now: datetime
    ) -> None:
        f = ImmutableDefaultFieldMutableOverrideFiling(
            id="test_id",
            created_at=datetime_now,
        )
        assert f.checksum == "override_checksum"

        f.checksum = "overwrite_checksum"
        f.is_zip = True
        assert f.checksum == "overwrite_checksum"
        assert f.is_zip is True

    def test_define_with_immutable_default_value_override_failed_multiple(
        self, datetime_now: datetime
    ) -> None:
        """親クラスのimmutableなDefault値は子クラスのdefault値の設定を許容しない（複数）"""
        # クラス定義時にエラーが発生することを確認
        with pytest.raises(FilingImmutableError) as fve:

            class ImmutableDefaultFieldOverrideFiling(ImmutableDefaultFieldFiling):
                checksum = "override_checksum"
                source = "override_source"
                additional_field = "override_additional_field"
                additional_field_2 = 987

        # 最初に検出されたフィールドがエラーに含まれる
        assert fve.value.fields == [
            "source",
            "additional_field",
            "additional_field_2",
        ]

    def test_initialize_with_immutable_default_value_override_failed(
        self, datetime_now: datetime
    ) -> None:
        """親クラスのimmutableなDefault値は子クラスのインスタンス化時のkwargs指定を許容しない"""
        with pytest.raises(FilingImmutableError) as fve:
            ImmutableDefaultFieldNoOverrideFiling(
                id="test_id",
                source="override_source",
                created_at=datetime_now,
            )
        assert fve.value.fields == ["source"]

    def test_overwrite_after_initialize_immutable_default_failed(
        self, datetime_now: datetime
    ) -> None:
        """親クラスのimmutableなDefault値は子クラスでインスタンス化後の代入を許容しない"""
        f = ImmutableDefaultFieldNoOverrideFiling(
            id="test_id",
            created_at=datetime_now,
        )
        with pytest.raises(FilingImmutableError) as fve:
            f.source = "overwrite_source"
        assert fve.value.fields == ["source"]

        with pytest.raises(FilingImmutableError) as fve:
            f.additional_field = "overwrite_additional_field"
        assert fve.value.fields == ["additional_field"]
