#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import defaultdict
from itertools import groupby
from pprint import pprint
from typing import List, Dict

from core.currency_converter import CurrencySalaryConverter
from core.models import EmploymentPeriod, Currency
from core.purchasing_power_converter import purchasing_power_converters
from core.salary_calculator.salary_calculator import SalaryCalculator, ConvertedSalary


def _get_all_stats(salaries: List[int]):
    key = float
    return {
        'min': min(salaries, key=key),
        'max': max(salaries, key=key),
        'sum': sum(map(key, salaries)),
        'avg': sum(map(key, salaries)) / len(salaries)
    }


def get_yearly_stats(periods: List[EmploymentPeriod],
                     currencies: List[Currency]):
    stats: Dict[int, Dict[Currency, Dict]] = defaultdict(dict)

    calculator = SalaryCalculator(CurrencySalaryConverter(), purchasing_power_converters)
    converted: ConvertedSalary = calculator.convert(periods,
                                                    currencies,
                                                    [])

    for year, monthly_salaries in groupby(converted.salaries.items(), key=lambda p: p[0].year):
        currency_to_monthly_amount_tuples = [item
                                             for monthly_grouped in monthly_salaries
                                             for item in monthly_grouped[1].items()]
        currency_to_monthly_amounts = defaultdict(list)
        for currency, monthly_amount in currency_to_monthly_amount_tuples:
            if monthly_amount:
                currency_to_monthly_amounts[currency].append(monthly_amount)

        for currency, monthly_amounts in currency_to_monthly_amounts.items():
            stats[year][currency] = _get_all_stats(monthly_amounts)
    return stats


def print_yearly_stats(periods: List[EmploymentPeriod],
                       currencies: List[Currency]):
    yearly_stats = get_yearly_stats(periods, currencies)
    yearly_usd_avg = dict()

    print('Yearly salary:')
    for year, grouped_by_currency in yearly_stats.items():
        print(year)
        for currency, all_stats in grouped_by_currency.items():
            print('\t', currency, '{:.0f}'.format(all_stats['sum']), '\t', all_stats)
            if currency == Currency.USD:
                yearly_usd_avg[year] = int(all_stats['avg'])
    print('Yearly USD average monthly salary:')
    pprint(yearly_usd_avg, width=20)
