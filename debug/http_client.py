import json

from fino_filing.collector._http_client import HttpClient as MyHttpClient
from fino_filing.collector.http import HttpClient

ENDPOINT = "https://httpbin.org/json"

client = HttpClient(user_agent="test")

res1 = client.get(ENDPOINT)
print(type(res1))
print(res1)


print("----------------------------------------------------------------")

my_client = MyHttpClient()

res = my_client.get(ENDPOINT)
print(type(res))
print(json.dumps(res, indent=4))
print(type(json.dumps(res, indent=4)))
print("----------------------------------------------------------------")
res = my_client.get_raw(ENDPOINT)
print(type(res))
print(res)
print(type(res.decode()))
print(res.decode())
print(type(json.loads(res.decode())))
print(json.loads(res.decode()))
print(type(json.loads(res)))
print(json.loads(res))


# print("----------------------------------------------------------------")
# edinet_client = EdinetClient(
#     config=EdinetConfig(api_key=os.getenv("EDINET_API_KEY") or "")
# )

# res_ed = edinet_client.get_document_list("2024-03-11", type=2)

# print(type(res_ed))
# print(json.dumps(res_ed, indent=4))
# print(type(json.dumps(res_ed, indent=4)))
