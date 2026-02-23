import pytest

from fino_filing.collection.error import CollectionChecksumMismatchError


class TestCollectionChecksumMismatchError:
    """
    CollectionChecksumMismatchErrorの振る舞いテスト
    """

    def test_collection_checksum_mismatch_error_message(self) -> None:
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
