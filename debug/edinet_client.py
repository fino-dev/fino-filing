import json
import os
from datetime import date

import fino_filing as ff
from fino_filing.collector.edinet import EdinetClient
from fino_filing.collector.edinet.enum import EDINET_DOCUMENT_LIST_TYPE

edinet_api_key = os.getenv("EDINET_API_KEY")

# print(edinet_api_key)

client = EdinetClient(ff.EdinetConfig(api_key=os.getenv("EDINET_API_KEY") or ""))


# print("----------------------------------------------------------------")
# print(type(client.get_document_list(date(2025, 4, 1), type=1)))
# print(json.dumps(client.get_document_list(date(2025, 4, 2), type=1), indent=4))
# print("----------------------------------------------------------------")
# # print(type(client.get_document_list(date(2025, 4, 2), type=2)))
# print(json.dumps(client.get_document_list(date(2025, 4, 2), type=2), indent=4))
# print(client.get_document_list(date(2025, 4, 2), type=2))
# print("----------------------------------------------------------------")

# filings = client.get_document_list(date(2025, 4, 2), type=2)
# print(type(filings["results"][10]["periodStart"]))
# print(filings["results"][10]["periodStart"])
# print(type(filings["results"][10]["submitDateTime"]))
# print(filings["results"][10]["submitDateTime"])

filings = client.get_document_list(
    date(2025, 4, 1), type=EDINET_DOCUMENT_LIST_TYPE.METADATA
)

print(json.dumps(filings, indent=4))
