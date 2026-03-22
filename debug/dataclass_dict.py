from dataclasses import asdict, dataclass


@dataclass
class Hoge:
    name: str
    age: int


hoge = Hoge(name="hoge", age=10)
print(hoge)
dict = asdict(hoge)
dict.pop("age")

print(dict)

print(hoge)
