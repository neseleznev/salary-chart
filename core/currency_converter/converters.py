from collections import defaultdict
from datetime import date
from typing import Dict, List

from currency_converter import CurrencyConverter, RateNotFoundError

from core.date_util import month_generator
from ..models import EmploymentPeriod, Currency

__all__ = ['CurrencySalaryConverter']

FULL_DATA_CURRENCY_RATES_DATA_URL = 'http://www.ecb.int/stats/eurofxref/eurofxref-hist.zip'


class CurrencySalaryConverter:

    def __init__(self):
        self._currency_converter = CurrencyConverter(FULL_DATA_CURRENCY_RATES_DATA_URL,
                                                     fallback_on_missing_rate=True)

    def convert(self, periods: List[EmploymentPeriod], new_currency: Currency) -> Dict[date, int]:
        salary = defaultdict(lambda: 0)

        for period in periods:
            for month in month_generator(period.begin, period.end):
                converted = self._convert(period, new_currency, month)
                if converted is None or salary[month] is None:
                    salary[month] = None
                else:
                    salary[month] += converted

        for key, value in salary.items():
            if value is not None:
                salary[key] = round(value)
        return salary

    def _convert(self, period: EmploymentPeriod, new_currency: Currency, dt: date):
        try:
            return self._currency_converter.convert(period.salary.amount,
                                                    period.salary.currency.name,
                                                    new_currency.name,
                                                    dt)
        except RateNotFoundError:
            return None
