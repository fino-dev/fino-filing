from typing import Any

# inの条件でkeyが存在するか確認する際に、値がNoneでもTrueになる
dictionary: dict[str, Any] = {"hoge": "fuga", "no": None}
print(dictionary["hoge"])
print("hoge" in dictionary)
print("no" in dictionary)
print("pika" in dictionary)
