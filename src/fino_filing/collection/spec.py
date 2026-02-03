import hashlib
from datetime import datetime
from typing import Protocol


class FilingIDStrategy(Protocol):
    """Filing ID生成戦略"""

    def generate_id(self, source: str, source_id: str, checksum: str) -> str:
        """ID生成"""
        ...

    def parse_id(self, filing_id: str) -> dict:
        """ID解析"""
        ...


class StandardIDStrategy:
    """標準ID戦略: {source}:{source_id}:{checksum_short}"""

    def generate_id(self, source: str, source_id: str, checksum: str) -> str:
        # checksum先頭8文字のみ使用（衝突リスク低い）
        checksum_short = checksum[:8]
        return f"{source}:{source_id}:{checksum_short}"

    def parse_id(self, filing_id: str) -> dict:
        parts = filing_id.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid filing_id format: {filing_id}")
        return {
            "source": parts[0],
            "source_id": parts[1],
            "checksum_short": parts[2],
        }


class SecureIDStrategy:
    """セキュアID戦略: {source}:{hash(source_id + checksum)}"""

    def generate_id(self, source: str, source_id: str, checksum: str) -> str:
        combined = f"{source_id}:{checksum}"
        secure_hash = hashlib.sha256(combined.encode()).hexdigest()[:16]
        return f"{source}:{secure_hash}"

    def parse_id(self, filing_id: str) -> dict:
        parts = filing_id.split(":")
        return {
            "source": parts[0],
            "secure_hash": parts[1],
        }


class RegistryPlacementStrategy(Protocol):
    """Registry配置戦略"""

    def get_registry_path(self, filing_metadata: dict) -> str:
        """Filing用のRegistry配置パスを返す"""
        ...

    def scan_pattern(self) -> str:
        """スキャン時の検索パターン"""
        ...


class DateBasedPlacement:
    """日付ベース: {source}/{year}/{month}/.fino_registry.json"""

    def __init__(self, registry_filename: str = ".fino_registry.json"):
        self.registry_filename = registry_filename

    def get_registry_path(self, filing_metadata: dict) -> str:
        source = filing_metadata["source"]
        submit_date = filing_metadata["submit_date"]

        if isinstance(submit_date, str):
            dt = datetime.fromisoformat(submit_date)
        else:
            dt = submit_date

        directory = f"{source}/{dt.year}/{dt.month:02d}"
        return f"{directory}/{self.registry_filename}"

    def scan_pattern(self) -> str:
        return f"**/{self.registry_filename}"


class SourceBasedPlacement:
    """Sourceベース: {source}/.fino_registry.json（全てroot直下）"""

    def __init__(self, registry_filename: str = ".fino_registry.json"):
        self.registry_filename = registry_filename

    def get_registry_path(self, filing_metadata: dict) -> str:
        source = filing_metadata["source"]
        return f"{source}/{self.registry_filename}"

    def scan_pattern(self) -> str:
        return f"*/{self.registry_filename}"


class HybridPlacement:
    """ハイブリッド: {source}/{year}/.fino_registry.json"""

    def get_registry_path(self, filing_metadata: dict) -> str:
        source = filing_metadata["source"]
        submit_date = datetime.fromisoformat(filing_metadata["submit_date"])
        return f"{source}/{submit_date.year}/.fino_registry.json"

    def scan_pattern(self) -> str:
        return "**/.fino_registry.json"
