from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import List, Dict

from ..currency_converter import CurrencySalaryConverter
from ..models import Currency, EmploymentPeriod
from ..purchasing_power_converter.base import BasePurchasingPowerSalaryConverter


@dataclass
class ConvertedSalary:
    salaries: Dict[date, Dict[Currency, int]]
    salaries_purchasing_power: Dict[date, Dict[Currency, int]]


class SalaryCalculator:

    def __init__(self,
                 currency_converter: CurrencySalaryConverter,
                 purchasing_power_converters: Dict[Currency, BasePurchasingPowerSalaryConverter]):
        self._currency_converter = currency_converter
        self._purchasing_power_converters = purchasing_power_converters

    def convert(self,
                periods: List[EmploymentPeriod],
                currencies: List[Currency],
                currencies_purchasing_power: List[Currency]) -> ConvertedSalary:

        salaries = self._get_salary_in_currencies(periods, currencies)
        salaries_purchasing_power = self._get_salary_in_purchasing_power(periods, currencies_purchasing_power)

        return ConvertedSalary(salaries, salaries_purchasing_power)

    def _get_salary_in_currencies(self, periods, currencies):
        result: Dict[date, Dict[Currency, int]] = defaultdict(dict)

        for currency in currencies:
            converted_salaries = self._currency_converter.convert(periods, currency)

            for dt, money_amount in converted_salaries.items():
                result[dt].update({currency: money_amount})
        return result

    def _get_salary_in_purchasing_power(self, periods, currencies):
        salary_in_currencies = self._get_salary_in_currencies(periods, currencies)

        result: Dict[date, Dict[Currency, int]] = defaultdict(dict)

        for currency in currencies:
            converter = self._purchasing_power_converters.get(currency)

            if converter:
                converted_salary = {dt: salary.get(currency) for dt, salary in salary_in_currencies.items()}

                salaries_adjusted_for_purchasing_power = converter.convert(converted_salary)

                for dt, money_amount in salaries_adjusted_for_purchasing_power.items():
                    result[dt].update({currency: money_amount})
        return result
