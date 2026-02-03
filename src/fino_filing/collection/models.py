import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)  # Immutable
class Filing:
    """Filing Entity(不変ID保持)"""

    filing_id: str  # 不変ID
    source: str  # edinet, edgar, tdnet
    source_id: str  # source側の識別子
    checksum: str  # SHA256
    document_type: str
    submit_date: datetime
    company_name: str
    metadata: dict
    _storage: Optional[object] = None  # 遅延ロード用
    _content_cache: Optional[bytes] = None

    def get_content(self) -> bytes:
        """Payload取得(遅延ロード)"""
        if self._content_cache is None:
            path = self.metadata.get("_path")
            if not path or not self._storage:
                raise ValueError("Cannot load content: missing path or storage")
            self._content_cache = self._storage.load(path)
        return self._content_cache

    def verify_checksum(self) -> bool:
        """Checksum検証"""
        content = self.get_content()
        actual = hashlib.sha256(content).hexdigest()
        return actual == self.checksum

    def to_dict(self) -> dict:
        """辞書形式(Registry保存用)"""
        return {
            "filing_id": self.filing_id,
            "source": self.source,
            "source_id": self.source_id,
            "checksum": self.checksum,
            "document_type": self.document_type,
            "submit_date": self.submit_date.isoformat(),
            "company_name": self.company_name,
            **self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict, storage=None):
        """辞書から復元"""
        return cls(
            filing_id=data["filing_id"],
            source=data["source"],
            source_id=data["source_id"],
            checksum=data["checksum"],
            document_type=data["document_type"],
            submit_date=datetime.fromisoformat(data["submit_date"]),
            company_name=data["company_name"],
            metadata={
                k: v
                for k, v in data.items()
                if k
                not in [
                    "filing_id",
                    "source",
                    "source_id",
                    "checksum",
                    "document_type",
                    "submit_date",
                    "company_name",
                ]
            },
            _storage=storage,
        )
