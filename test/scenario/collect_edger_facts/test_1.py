"""シナリオ: Collection の初期化（module の test_init と重複するがシナリオとして配置）"""

from pathlib import Path

import pytest

from fino_filing import (
    Collection,
    EdgarCompanyFactsFiling,
    EdgarConfig,
    EdgarFactsCollector,
    Field,
)


@pytest.mark.scenario
@pytest.mark.edgar
@pytest.mark.collector
class TestScenario_CollectEdgarFacts:
    """Scenario: Collect Edgar Facts"""

    def test_collect_edgar_facts_with_single_cik(
        self, temp_collection: Collection
    ) -> None:
        """CIK が 1つ指定して収集できる"""

        collector = EdgarFactsCollector(
            collection=temp_collection,
            config=EdgarConfig(user_agent_email="test@example.com"),
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
        assert collected[0][0].source == "Edgar"
        path = Path(collected[0][1])
        assert path is not None
        assert path.exists()

        # Collectionからgetできる
        filing, content, path = temp_collection.get(collected[0][0].id)
        assert filing is not None
        assert filing.source == "Edgar"
        assert content is not None

        assert path is not None
        assert Path(path).resolve() == Path(collected[0][1]).resolve()

        # Collectionからsearchできる（右辺でクラス参照）
        filings = temp_collection.search(
            expr=(Field("source") == EdgarCompanyFactsFiling.source)
        )
        filing = filings[0]
        assert filing is not None
        assert isinstance(filing, EdgarCompanyFactsFiling)
        assert filing.source == "Edgar"
        assert filing.id == collected[0][0].id
        assert filing.name == collected[0][0].name
        assert filing.created_at == collected[0][0].created_at
        assert filing.format == "json"
        assert filing.is_zip is False
        assert filing.edgar_resource_kind == "companyfacts"

        assert filing.cik == "0001652044"
        assert filing.filer_name == "Alphabet Inc."

        # 左辺でモデルフィールド（デフォルトあり）でも search 可能
        filings = temp_collection.search(
            expr=(EdgarCompanyFactsFiling.source == "Edgar")
        )
        assert len(filings) == 1 and filings[0].id == collected[0][0].id
