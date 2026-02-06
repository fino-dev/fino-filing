from __future__ import annotations

import hashlib
from datetime import datetime
from typing import TYPE_CHECKING, Any

from .field import Field
from .meta import ModelMeta

if TYPE_CHECKING:
    pass


class Filing(metaclass=ModelMeta):
    """
    Filing Document（スキーマレス）

    責務:
        - データ保持
        - フィールド定義
        - 拡張可能モデル提供

    Collectionに依存しない。

    Usage:
        # モデルベース
        class EDINETFiling(Filing):
            filer_name = Field(str, indexed=True)
            revenue = Field(float)

        # スキーマレス
        filing = Filing(filing_id="...", source="custom")
        filing.set("custom_field", "value")
    """

    # ========== Core Fields（物理カラム化推奨） ==========

    filing_id = Field("filing_id", str, indexed=True, description="Filing ID")
    source = Field("source", str, indexed=True, description="Data source")
    checksum = Field("checksum", str, indexed=True, description="SHA256 checksum")
    filing_name = Field("filing_name", str, indexed=True, description="File name")
    is_zip = Field("is_zip", bool, indexed=True, description="ZIP flag")
    created_at = Field(
        "created_at", datetime, indexed=True, description="Created timestamp"
    )
    path = Field("path", str, indexed=True, description="Storage path")

    def __init__(self, **kwargs):
        """
        Args:
            **kwargs: フィールド値
        """
        # データストア（フラット）
        self._data = {}

        # 内部管理用
        self._storage = kwargs.pop("_storage", None)
        self._content_cache = None

        # kwargs から値を設定
        for key, value in kwargs.items():
            self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        フィールド取得

        Args:
            key: フィールド名
            default: デフォルト値

        Returns:
            フィールド値
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        """
        フィールド設定

        Args:
            key: フィールド名
            value: 値
        """
        self._data[key] = value

    def get_content(self) -> bytes:
        """
        Payload取得（遅延ロード）

        Returns:
            バイナリコンテンツ
        """
        if self._content_cache is None:
            if not self._storage:
                raise ValueError("Storage not set")

            path = self._data.get("path")
            if not path:
                raise ValueError("Path not set")

            self._content_cache = self._storage.load(path)

        return self._content_cache

    def verify_checksum(self) -> bool:
        """
        Checksum検証

        Returns:
            検証結果
        """
        content = self.get_content()
        actual = hashlib.sha256(content).hexdigest()
        expected = self._data.get("checksum")

        return actual == expected

    def to_dict(self) -> dict[str, Any]:
        """
        辞書化（完全フラット）

        Returns:
            フィールド辞書
        """
        result = {}

        for key, value in self._data.items():
            # datetime → ISO文字列変換
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value

        return result

    @classmethod
    def from_dict(cls, data: dict, storage: Any = None) -> Filing:
        """
        辞書から復元

        Args:
            data: フィールド辞書
            storage: Storageインスタンス

        Returns:
            Filingインスタンス
        """
        # datetime復元
        data_copy = data.copy()

        if "created_at" in data_copy and isinstance(data_copy["created_at"], str):
            data_copy["created_at"] = datetime.fromisoformat(data_copy["created_at"])

        return cls(_storage=storage, **data_copy)

    @classmethod
    def get_indexed_fields(cls) -> list[str]:
        """
        物理カラム化されるフィールド一覧

        Returns:
            フィールド名リスト
        """
        return [field.name for field in cls._fields.values() if field.indexed]

    def __repr__(self):
        filing_id = self._data.get("filing_id", "???")
        source = self._data.get("source", "???")
        return f"{self.__class__.__name__}(filing_id={filing_id!r}, source={source!r})"


# ========== Template Models ==========


class EDINETFiling(Filing):
    """EDINET Filing Template"""

    # EDINET固有フィールド（任意）
    edinet_code = Field(str, description="EDINETコード")
    sec_code = Field(str, description="証券コード")
    jcn = Field(str, description="法人番号")
    filer_name = Field(str, description="提出者名")
    ordinance_code = Field(str, description="府令コード")
    form_code = Field(str, description="様式コード")
    doc_description = Field(str, description="書類名")
    period_start = Field(datetime, description="期間開始")
    period_end = Field(datetime, description="期間終了")
    submit_datetime = Field(datetime, description="提出日時")


class EDGARFiling(Filing):
    """EDGAR Filing Template"""

    # EDGAR固有フィールド（任意）
    cik = Field(str, description="CIK")
    accession_number = Field(str, description="Accession Number")
    company_name = Field(str, description="Company Name")
    form_type = Field(str, description="Form Type")
    filing_date = Field(datetime, description="Filing Date")
    period_of_report = Field(datetime, description="Period of Report")
    sic_code = Field(str, description="SIC Code")
    state_of_incorporation = Field(str, description="State of Incorporation")
    fiscal_year_end = Field(str, description="Fiscal Year End")


# ========== ユーザー拡張例 ==========


class MyCustomFiling(EDINETFiling):
    """ユーザー定義Filing（拡張）"""

    # カスタムフィールド
    ticker = Field(str, indexed=True, description="Ticker Symbol")
    revenue = Field(float, description="Revenue")
    industry = Field(str, description="Industry")
    market_cap = Field(float, description="Market Cap")
    analyst_rating = Field(str, description="Analyst Rating")
