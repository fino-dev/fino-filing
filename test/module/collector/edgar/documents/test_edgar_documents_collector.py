from pathlib import Path

from fino_filing import Collection, EdgarConfig, EdgarDocumentsCollector


class TestEdgarDocumentsCollector:
    """
    EdgarDocumentsCollector Test
    """

    def test_collector_initialize_with_config(
        self,
        temp_collection: tuple[Collection, Path],
        edgar_config: EdgarConfig,
    ) -> None:
        """Collector の初期化が config を渡して client に反映される"""
        collection, _ = temp_collection
        collector = EdgarDocumentsCollector(collection=collection, config=edgar_config)
        assert collector._client._headers["User-Agent"] == "test@example.com"
