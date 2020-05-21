import calendar
from datetime import date
from typing import Generator


def month_generator(begin: date, end: date, month_step: int = 1) -> Generator[date, None, None]:
    current = begin
    while current <= end:
        yield current
        current = add_months(current, month_step)


def add_months(source_date: date, month_step: int) -> date:
    month = source_date.month - 1 + month_step
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)
