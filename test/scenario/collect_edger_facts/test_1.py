"""シナリオ: Collection の初期化（module の test_init と重複するがシナリオとして配置）"""

from pathlib import Path

import pytest

from fino_filing import Collection, EdgerConfig, EdgerFactsCollector


@pytest.mark.scenario
@pytest.mark.edger
@pytest.mark.collector
class TestScenario_CollectEdgerFacts:
    """Scenario: Collect Edger Facts"""

    def test_collect_edger_facts_with_single_cik(
        self, temp_collection: Collection
    ) -> None:
        """CIK が 1つ指定して収集できる"""

        collector = EdgerFactsCollector(
            collection=temp_collection,
            config=EdgerConfig("test@example.com"),
        )

        print("===================================")
        print("Alphabet Inc. (cik: 0001652044)")
        print("===================================")
        # 収集可能である
        collected = collector.collect(cik_list=["0001652044"])

        print(f"collected number: {len(collected)}")
        for filing, path in collected:
            filing = collected[0][0]
            path = collected[0][1]
            print(f"filing: {filing.name}")
            print(f"path: {path}")
            print("-----------------------------------")

        # 収集結果が 1 件であり、指定のpathに保存されている
        assert len(collected) == 1
        assert collected[0][0].source == "EDGAR"
        path = Path(collected[0][1])
        assert path is not None
        assert path.exists()

        # Collectionから取得できる
        filing, content, path = temp_collection.get(collected[0][0].id)
        assert filing is not None
        assert filing.source == "EDGAR"
        assert content is not None

        assert path is not None
        # get() が返す path は絶対パス。add の戻り値も絶対パスのため一致する。
        assert Path(path).resolve() == Path(collected[0][1]).resolve()
