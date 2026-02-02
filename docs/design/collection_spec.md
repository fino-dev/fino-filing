# fino Collection / Spec 設計方針

1. 用語整理と基本スタンス
   Spec とは

- payload（保存された実体）から意味を導出するための解釈仕様
- データではなく振る舞い（behavior）
- 永続化されない（ただし評価結果のキャッシュは可）
- payload と code から毎回導出される

fino は spec の「内容」には関与しない
fino は spec を差し込むための枠（interface）だけを提供する

```python
import fino-eidnet-collector as fec, SpecField, CustomField

fun ticker_generate(filing: FilingMetadata) -> str:
    ticker = mapping_ticker_from_sec(filing.sec_code)

    return ticker

collection_spec = fec.CollectionSpec(
    partition=[
        EdinetSpecAttribute.SEC_CODE,
        EdinetSpecAttribute.DOCUMENT_TYPE,
        EdinetSpecAttribute.PERIOD_START,
        CustomSpecField("ticker", ticker_generate)
    ],
    file_name=[
        EdinetSpecAttribute.DOCUMENT_ID,
        EdinetSpecAttribute.FORMAT_TYPE
    ]
)

collection = fec.Collection(type="s3", spec=collection_spec)

edinet = fec.Edinet(api_key="hogehgoehogheohoge", collection=collection)
```

\*\*

- file pathの衝突はdoc_idをfile_nameに必須にすることで回避する
- format typeによる衝突はdocument idで回避できない（単一doc idで複数のformatが存在する）ため、ファイルの拡張子prefixとして自動挿入する
- \*\*
