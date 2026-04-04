from pathlib import Path

from fino_filing import Collection, EdgerConfig, EdgerDocumentsCollector


class TestEdgerDocumentsCollector:
    """
    EdgerDocumentsCollector Test
    """

    def test_collector_initialize_with_config(
        self,
        temp_collection: tuple[Collection, Path],
        edger_config: EdgerConfig,
    ) -> None:
        """Collector の初期化が config を渡して client に反映される"""
        collection, _ = temp_collection
        collector = EdgerDocumentsCollector(collection=collection, config=edger_config)
        assert collector._client._headers["User-Agent"] == "test@example.com"
