from datetime import date, datetime

feb29 = date(2024, 2, 29)
feb28 = date(2024, 2, 28)

print(feb29 > feb28)

print(type(feb28))
print(feb28)
print(type(feb28.strftime("%Y-%m-%d")))
print(feb28.strftime("%Y-%m-%d"))
print(type(datetime.strptime(feb28.strftime("%Y-%m-%d"), "%Y-%m-%d").date()))
print(datetime.strptime(feb28.strftime("%Y-%m-%d"), "%Y-%m-%d"))
