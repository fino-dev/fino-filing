"""シナリオ: Collection の初期化（module の test_init と重複するがシナリオとして配置）"""

import pytest

from fino_filing import Collection, EdgerConfig, EdgerFactsCollector


@pytest.mark.scenario
@pytest.mark.edger
@pytest.mark.collector
class TestScenario_CollectEdgerFacts:
    """Scenario: Collect Edger Facts"""

    def test_collection_init_with_storage_and_catalog(self) -> None:
        """Collection(storage, catalog) で初期化できる"""

        collection = Collection()

        collector = EdgerFactsCollector(
            collection=collection, config=EdgerConfig("test@example.com")
        )

        collected = collector.collect(cik_list=["320193"])
        assert len(collected) == 1
        assert collected[0][0].source == "EDGAR"
