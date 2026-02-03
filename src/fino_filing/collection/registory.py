import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Iterator, List


@dataclass
class FilingMemento:
    """Registry保存用の最小metadata"""

    filing_id: str
    source: str
    source_id: str
    checksum: str
    filename: str  # payloadのファイル名
    document_type: str
    submit_date: str
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class Registry:
    """Directory-local registry（1ディレクトリ分）"""

    def __init__(self, directory: str, registry_path: str):
        self.directory = directory
        self.registry_path = registry_path
        self.filings: List[FilingMemento] = []

    def add(self, memento: FilingMemento):
        """Filing追加（重複チェック）"""
        if any(f.filing_id == memento.filing_id for f in self.filings):
            # 既存の場合は更新
            self.filings = [
                f if f.filing_id != memento.filing_id else memento for f in self.filings
            ]
        else:
            self.filings.append(memento)

    def save(self, storage):
        """Registryファイル保存"""
        data = {
            "version": "1.0",
            "directory": self.directory,
            "updated_at": datetime.now().isoformat(),
            "filings": [f.to_dict() for f in self.filings],
        }
        content = json.dumps(data, indent=2, ensure_ascii=False).encode()
        storage.save(self.registry_path, content)

    @classmethod
    def load(cls, registry_path: str, storage) -> "Registry":
        """Registryファイル読み込み"""
        content = storage.load(registry_path)
        data = json.loads(content.decode())

        registry = cls(
            directory=data["directory"],
            registry_path=registry_path,
        )
        registry.filings = [FilingMemento.from_dict(f) for f in data["filings"]]
        return registry


class RegistryManager:
    """Registry管理（Mementoパターン）"""

    def __init__(self, storage, spec):
        self.storage = storage
        self.spec = spec

    def register(self, filing, directory: str):
        """Filingをregistryに登録"""
        # Registry読み込みor新規作成
        registry_path = self.spec.registry_strategy.get_registry_path(filing.to_dict())

        try:
            registry = Registry.load(registry_path, self.storage)
        except:
            registry = Registry(directory, registry_path)

        # Memento作成
        memento = FilingMemento(
            filing_id=filing.filing_id,
            source=filing.source,
            source_id=filing.source_id,
            checksum=filing.checksum,
            filename=filing.metadata.get("_filename", ""),
            document_type=filing.document_type,
            submit_date=filing.submit_date.isoformat(),
            created_at=datetime.now().isoformat(),
        )

        registry.add(memento)
        registry.save(self.storage)

    def scan_all(self) -> Iterator[Registry]:
        """全Registryスキャン"""
        pattern = self.spec.registry_strategy.scan_pattern()

        for registry_path in self.storage.list(pattern):
            try:
                yield Registry.load(registry_path, self.storage)
            except Exception as e:
                print(f"Warning: Failed to load registry {registry_path}: {e}")

    def rebuild_from_payloads(self):
        """Payloadから全Registry再構築（災害復旧用）"""
        # 全payloadスキャン → checksum計算 → registry再生成
        # 実装は複雑になるため省略（概念のみ提示）
        raise NotImplementedError("Disaster recovery feature")


@dataclass
class FilingMemento:
    """Registry保存用の最小metadata"""

    filing_id: str
    source: str
    source_id: str
    checksum: str
    filename: str  # payloadのファイル名
    document_type: str
    submit_date: str
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class Registry:
    """Directory-local registry（1ディレクトリ分）"""

    def __init__(self, directory: str, registry_path: str):
        self.directory = directory
        self.registry_path = registry_path
        self.filings: List[FilingMemento] = []

    def add(self, memento: FilingMemento):
        """Filing追加（重複チェック）"""
        if any(f.filing_id == memento.filing_id for f in self.filings):
            # 既存の場合は更新
            self.filings = [
                f if f.filing_id != memento.filing_id else memento for f in self.filings
            ]
        else:
            self.filings.append(memento)

    def save(self, storage):
        """Registryファイル保存"""
        data = {
            "version": "1.0",
            "directory": self.directory,
            "updated_at": datetime.now().isoformat(),
            "filings": [f.to_dict() for f in self.filings],
        }
        content = json.dumps(data, indent=2, ensure_ascii=False).encode()
        storage.save(self.registry_path, content)

    @classmethod
    def load(cls, registry_path: str, storage) -> "Registry":
        """Registryファイル読み込み"""
        content = storage.load(registry_path)
        data = json.loads(content.decode())

        registry = cls(
            directory=data["directory"],
            registry_path=registry_path,
        )
        registry.filings = [FilingMemento.from_dict(f) for f in data["filings"]]
        return registry


class RegistryManager:
    """Registry管理（Mementoパターン）"""

    def __init__(self, storage, spec):
        self.storage = storage
        self.spec = spec

    def register(self, filing, directory: str):
        """Filingをregistryに登録"""
        # Registry読み込みor新規作成
        registry_path = self.spec.registry_strategy.get_registry_path(filing.to_dict())

        try:
            registry = Registry.load(registry_path, self.storage)
        except:
            registry = Registry(directory, registry_path)

        # Memento作成
        memento = FilingMemento(
            filing_id=filing.filing_id,
            source=filing.source,
            source_id=filing.source_id,
            checksum=filing.checksum,
            filename=filing.metadata.get("_filename", ""),
            document_type=filing.document_type,
            submit_date=filing.submit_date.isoformat(),
            created_at=datetime.now().isoformat(),
        )

        registry.add(memento)
        registry.save(self.storage)

    def scan_all(self) -> Iterator[Registry]:
        """全Registryスキャン"""
        pattern = self.spec.registry_strategy.scan_pattern()

        for registry_path in self.storage.list(pattern):
            try:
                yield Registry.load(registry_path, self.storage)
            except Exception as e:
                print(f"Warning: Failed to load registry {registry_path}: {e}")

    def rebuild_from_payloads(self):
        """Payloadから全Registry再構築（災害復旧用）"""
        # 全payloadスキャン → checksum計算 → registry再生成
        # 実装は複雑になるため省略（概念のみ提示）
        raise NotImplementedError("Disaster recovery feature")
