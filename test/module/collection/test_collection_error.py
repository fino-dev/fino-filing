import pytest

from fino_filing.collection.error import CollectionChecksumMismatchError


class TestCollectionChecksumMismatchError:
    """
    CollectionChecksumMismatchError. 観点: 異常系（例外の属性が仕様どおりであること）
    """

    def test_collection_checksum_mismatch_error_message(self) -> None:
        """仕様: filing_id, actual_checksum, expected_checksum を含む。検証: 例外型と message にそれらが含まれる"""
        with pytest.raises(CollectionChecksumMismatchError) as e:
            raise CollectionChecksumMismatchError(
                filing_id="test_filing_id",
                actual_checksum="test_actual_checksum",
                expected_checksum="test_expected_checksum",
            )
        assert (
            e.value.message
            == "[Fino Filing] Checksum mismatch filing id: test_filing_id, actual checksum: test_actual_checksum, expected checksum: test_expected_checksum"
        )
