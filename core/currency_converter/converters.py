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
                                                     fallback_on_missing_rate=True,
                                                     # RUB rate could not be found in 2022-04 and later on,
                                                     # thus these dates are considered wrong (out of known interval)
                                                     fallback_on_wrong_date=False)

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
            conventional_usd_rub_rate = self.get_conventional_usd_rub_rate(dt)

            if conventional_usd_rub_rate:
                if new_currency == Currency.RUB:
                    usd_amount = self._currency_converter.convert(period.salary.amount,
                                                                  period.salary.currency.name,
                                                                  Currency.USD.name,
                                                                  dt)
                    return conventional_usd_rub_rate * usd_amount
                if period.salary.currency == Currency.RUB:
                    usd_amount = 1. / conventional_usd_rub_rate * period.salary.amount
                    return self._currency_converter.convert(usd_amount,
                                                            Currency.USD.name,
                                                            new_currency.name,
                                                            dt)
            return None

    @staticmethod
    def get_conventional_usd_rub_rate(conversion_date):
        """
        Source: https://www.x-rates.com/average/?from=USD&to=RUB&amount=1&year=2023
        """
        if conversion_date >= date(2023, 11, 1):
            return 92.80  # TODO update
        if conversion_date >= date(2023, 10, 1):
            return 97.22
        if conversion_date >= date(2023, 9, 1):
            return 96.44
        if conversion_date >= date(2023, 8, 1):
            return 95.60
        if conversion_date >= date(2023, 7, 1):
            return 90.51
        if conversion_date >= date(2023, 6, 1):
            return 83.04
        if conversion_date >= date(2023, 5, 1):
            return 78.96
        if conversion_date >= date(2023, 4, 1):
            return 80.88
        if conversion_date >= date(2023, 3, 1):
            return 76.28
        if conversion_date >= date(2023, 2, 1):
            return 73.13
        if conversion_date >= date(2023, 1, 1):
            return 70.06
        if conversion_date >= date(2022, 12, 1):
            return 65.63
        if conversion_date >= date(2022, 11, 1):
            return 61.02
        if conversion_date >= date(2022, 10, 1):
            return 61.51
        if conversion_date >= date(2022, 9, 1):
            return 60.19
        if conversion_date >= date(2022, 8, 1):
            return 60.80
        if conversion_date >= date(2022, 7, 1):
            return 59.14
        if conversion_date >= date(2022, 6, 1):
            return 58.01
        if conversion_date >= date(2022, 5, 1):
            return 65.79
        if conversion_date >= date(2022, 4, 1):
            return 80.93
        return None
