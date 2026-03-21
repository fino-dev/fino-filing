from datetime import datetime, timedelta

import pytest

from fino_filing import Filing


@pytest.mark.module
@pytest.mark.filing
class TestFiling_GenerateId:
    common = dict(
        source="test_source",
        checksum="test_checksum",
        name="test_name",
        is_zip=False,
        format="xbrl",
    )

    def test_filing_id_generated_deterministically(self) -> None:
        """同一の値で同一のIDが生成されることを確認"""
        id1 = Filing._generate_id(self.common)
        id2 = Filing._generate_id(self.common)
        assert id1 == id2

    def test_filing_id_uses_only_identifier_fields_when_marked(self) -> None:
        """
        Field(identifier=True) のFieldがid ハッシュに使われる
        - FilingのidentifierなField（source, name, is_zip, format）によりhash化されることを確認
        - checksum, created_at はhash化に含まれないことを確認
        """
        common_id = Filing._generate_id(self.common)
        diff_source_id = Filing._generate_id(self.common | {"source": "diff_source"})
        diff_name_id = Filing._generate_id(self.common | {"name": "diff_name"})
        diff_is_zip_id = Filing._generate_id(self.common | {"is_zip": True})
        diff_format_id = Filing._generate_id(self.common | {"format": "diff_format"})
        assert common_id != diff_source_id
        assert common_id != diff_name_id
        assert common_id != diff_is_zip_id
        assert common_id != diff_format_id

        diff_checksum_id = Filing._generate_id(
            self.common | {"checksum": "diff_checksum"}
        )
        assert common_id == diff_checksum_id

        diff_created_at_id = Filing._generate_id(
            self.common | {"created_at": datetime.now() + timedelta(seconds=1)}
        )
        assert common_id == diff_created_at_id
