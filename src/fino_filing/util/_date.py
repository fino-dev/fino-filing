from datetime import date


def date_to_str(date: date) -> str:
    return date.strftime("%Y-%m-%d")
