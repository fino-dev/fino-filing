"""Scenario: Collection retrieval when the filing id is unknown."""

import pytest

from fino_filing.collection.collection import Collection


@pytest.mark.scenario
@pytest.mark.collection
class TestScenario_GetUnknownId:
    """Scenario: Unknown id retrieval Test"""

    def test_get_returns_none_tuple_for_unknown_id(
        self, temp_collection: Collection
    ) -> None:
        """存在しない ID に対して get / get_filing / get_content が空を返す"""
        filing, content, path = temp_collection.get("no_such_filing")
        assert filing is None
        assert content is None
        assert path is None
        assert temp_collection.get_filing("no_such_filing") is None
        assert temp_collection.get_content("no_such_filing") is None
