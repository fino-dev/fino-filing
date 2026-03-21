import os

import fino_filing as ff
from fino_filing.collector.edinet import EdinetClient

edinet_api_key = os.getenv("EDINET_API_KEY")

print(edinet_api_key)

client = EdinetClient(ff.EdinetConfig(api_key=os.getenv("EDINET_API_KEY") or ""))


print(client.get_document_list("2025-01-01"))
