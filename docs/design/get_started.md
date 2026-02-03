# Packageのインターフェース

## ユースケース

### 1. Getting Started Usecase

```python
# simple local usecase
import fino-filing as fec

# decide wheare to collect filings. it's depending on your usecase and environmnet
collection = fec.Collection(root_path="~/.edinet_file")

edinet = fec.Edinet(api_key="hogehgoehogheohoge", collection=collection)
edinet.sync_catalog()

result = edinet.collect(form_type=FormatType.ANNUAL)
result.filings[0] # Filing Class with file path
filing = filings[0]
filing_name = filing.name
filing_path = filing.path # easy to access file from result
file = filing.open()


collection.search(sec_code="1111")
collection.get(docd="hgoehgeo")

result.collection # provide same collection object from collect func result
```
