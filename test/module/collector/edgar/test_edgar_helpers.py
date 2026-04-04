import pytest
from fino_filing.collector.edgar._helpers import (
    _build_company_facts_json_file_name,
    _build_recent_submissions_json_file_name,
)


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edgar
class TestEdgarHelpers:
    class TestBuildRecentSubmissionsJsonFileName:
        def test_10_cik(self) -> None:
            """ """
            assert (
                _build_recent_submissions_json_file_name("1234567890")
                == "CIK1234567890-submissions.json"
            )

        def test_empty_cik(self) -> None:
            """ """
            assert (
                _build_recent_submissions_json_file_name("")
                == "CIK0000000000-submissions.json"
            )

    class TestBuildCompanyFactsJsonFileName:
        def test_10_cik(self) -> None:
            """ """
            assert (
                _build_company_facts_json_file_name("1234567890")
                == "CIK1234567890-companyfacts.json"
            )

        def test_empty_cik(self) -> None:
            """ """
            assert (
                _build_company_facts_json_file_name("")
                == "CIK0000000000-companyfacts.json"
            )
