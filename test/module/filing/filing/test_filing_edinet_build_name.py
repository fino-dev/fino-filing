"""EDINETFiling.build_name のテスト。"""

import pytest

from fino_filing.filing.error import FilingRequiredError
from fino_filing.filing.filing_edinet import EDINETFiling


@pytest.mark.module
@pytest.mark.filing
@pytest.mark.edinet
class TestEDINETFilingBuildName:
    """EDINETFiling.build_name の名前組み立てルールを検証する。"""

    def test_build_name_doc_id_and_description_and_format(self) -> None:
        assert (
            EDINETFiling.build_name("S100", "有価証券報告書", "pdf")
            == "S100_有価証券報告書.pdf"
        )

    def test_build_name_doc_id_only(self) -> None:
        assert EDINETFiling.build_name("S100", None, "xbrl") == "S100.xbrl"

    def test_build_name_description_only(self) -> None:
        assert (
            EDINETFiling.build_name(None, "四半期報告書", "zip") == "四半期報告書.zip"
        )

    def test_build_name_skips_empty_doc_id_string(self) -> None:
        assert EDINETFiling.build_name("", "書類名", "pdf") == "書類名.pdf"

    def test_build_name_skips_empty_description_string(self) -> None:
        assert EDINETFiling.build_name("S200", "", "csv") == "S200.csv"

    def test_build_name_empty_format_omits_suffix(self) -> None:
        assert EDINETFiling.build_name("S1", None, "") == "S1"

    def test_build_name_empty_none_format_omits_suffix(self) -> None:
        assert EDINETFiling.build_name("S1", "", "") == "S1"

    def test_build_name_none_format_omits_suffix(self) -> None:
        assert EDINETFiling.build_name("S1", None, None) == "S1"

    def test_build_name_requires_doc_id_or_description(self) -> None:
        with pytest.raises(FilingRequiredError):
            EDINETFiling.build_name(None, None, "pdf")

    def test_build_name_requires_non_empty_base(self) -> None:
        with pytest.raises(FilingRequiredError):
            EDINETFiling.build_name("", "", "pdf")
