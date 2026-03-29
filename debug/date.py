import fino_filing.collector.edinet._helpers as helpers

# feb29 = date(2024, 2, 29)
# feb28 = date(2024, 2, 28)

# print(feb29 > feb28)

# print(type(feb28))
# print(feb28)
# print(type(feb28.strftime("%Y-%m-%d")))
# print(feb28.strftime("%Y-%m-%d"))
# print(type(datetime.strptime(feb28.strftime("%Y-%m-%d"), "%Y-%m-%d").date()))
# print(datetime.strptime(feb28.strftime("%Y-%m-%d"), "%Y-%m-%d"))


edinet_datetime_string = "2025-04-02 09:19"

# edinet_date_string = "20250711"

# print("=================-")

# print(datetime.strptime(edinet_datetime_string, "%Y-%m-%d %H:%M"))
print(type(helpers._parse_edinet_datetime(edinet_datetime_string)))

# try:
#     print(datetime.strptime(edinet_date_string, "%Y-%m-%d").date())
# except (ValueError, TypeError):
#     print("ValueError: Invalid date string: ", edinet_date_string)
