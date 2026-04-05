"""EDINETFiling.build_default_name のテスト。"""

import pytest

from fino_filing.filing.error import FilingRequiredError
from fino_filing.filing.filing_edinet import EDINETFiling


@pytest.mark.module
@pytest.mark.filing
@pytest.mark.edinet
class TestEDINETFilingBuildName:
    """EDINETFiling.build_default_name の名前組み立てルールを検証する。"""

    def test_build_default_name_doc_id_and_description_and_format(self) -> None:
        assert (
            EDINETFiling.build_default_name("S100", "有価証券報告書", "pdf", False)
            == "S100_有価証券報告書.pdf"
        )

    def test_build_default_name_doc_id_only(self) -> None:
        assert (
            EDINETFiling.build_default_name("S100", None, "xbrl", False) == "S100.xbrl"
        )

    def test_build_default_name_description_only(self) -> None:
        assert (
            EDINETFiling.build_default_name(None, "四半期報告書", "zip", False)
            == "四半期報告書.zip"
        )

    def test_build_default_name_skips_empty_doc_id_string(self) -> None:
        assert (
            EDINETFiling.build_default_name("", "書類名", "pdf", False) == "書類名.pdf"
        )

    def test_build_default_name_skips_empty_description_string(self) -> None:
        assert EDINETFiling.build_default_name("S200", "", "csv", False) == "S200.csv"

    def test_build_default_name_empty_format_omits_suffix(self) -> None:
        assert EDINETFiling.build_default_name("S1", None, "", False) == "S1"

    def test_build_default_name_empty_none_format_omits_suffix(self) -> None:
        assert EDINETFiling.build_default_name("S1", "", "", False) == "S1"

    def test_build_default_name_none_format_omits_suffix(self) -> None:
        assert EDINETFiling.build_default_name("S1", None, None, False) == "S1"

    def test_build_default_name_requires_doc_id_or_description(self) -> None:
        with pytest.raises(FilingRequiredError):
            EDINETFiling.build_default_name(None, None, "pdf", False)

    def test_build_default_name_requires_non_empty_base(self) -> None:
        with pytest.raises(FilingRequiredError):
            EDINETFiling.build_default_name("", "", "pdf", False)

    def test_build_default_name_zip_suffix(self) -> None:
        assert (
            EDINETFiling.build_default_name("S100", "有価証券報告書", "pdf", True)
            == "S100_有価証券報告書.zip"
        )
        assert (
            EDINETFiling.build_default_name("S100", "有価証券報告書", "", True)
            == "S100_有価証券報告書.zip"
        )
        assert (
            EDINETFiling.build_default_name("S100", "有価証券報告書", None, True)
            == "S100_有価証券報告書.zip"
        )
