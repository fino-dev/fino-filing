"""EdgerFactsCollector: ネットワークなしで _parse_response / _build_filing を検証する。"""

import pytest

from fino_filing import Collection, EDGARCompanyFactsFiling, EdgerConfig, EdgerFactsCollector


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edger
class TestEdgerFactsCollector_ParseBuild:
    """EdgerFactsCollector. 観点: EDGARCompanyFactsFiling 生成"""

    def test_parse_and_build_produces_company_facts_filing(
        self, temp_collection: Collection
    ) -> None:
        """_parse_response / _build_filing が EDGARCompanyFactsFiling を返す"""
        collector = EdgerFactsCollector(
            collection=temp_collection,
            config=EdgerConfig(user_agent_email="test@example.com"),
        )
        meta = {
            "cik": "0001652044",
            "company_name": "Alphabet Inc.",
            "sic_code": "7370",
            "state_of_incorporation": "DE",
            "fiscal_year_end": "12-31",
            "format": "json",
            "primary_name": "CIK0001652044-companyfacts.json",
        }
        parsed = collector._parse_response(meta)
        filing = collector._build_filing(parsed, b"{}")
        assert isinstance(filing, EDGARCompanyFactsFiling)
        assert filing.cik == "0001652044"
        assert filing.company_name == "Alphabet Inc."
        assert filing.format == "json"
