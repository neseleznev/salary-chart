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

    _print_yearly_salary(yearly_stats)
    for currency in currencies:
        _print_year_to_year_monthly_average_change(yearly_stats, currency_to_print=currency)


def _print_yearly_salary(yearly_stats):
    print('Yearly salary:')
    for year, grouped_by_currency in yearly_stats.items():
        print(year)
        for currency, all_stats in grouped_by_currency.items():
            print('\t', currency, '{:.0f}'.format(all_stats['sum']), '\t', all_stats)
    print()


def _print_year_to_year_monthly_average_change(yearly_stats, currency_to_print):
    print('Year-to-year average monthly salary change:')
    yearly_avg = get_monthly_average_by_years(yearly_stats, currency_to_print)
    salary_format = '{:7,d}'

    result = dict()
    yearly_avg_items = list(yearly_avg.items())
    first_year, last_year_sum = yearly_avg_items[0]
    result[first_year] = (salary_format + ' {}').format(last_year_sum, currency_to_print.name)

    for i in range(1, len(yearly_avg_items)):
        current_year_item = yearly_avg_items[i]
        current_year, current_sum = current_year_item
        percent_change = int((current_sum / last_year_sum - 1) * 100)
        result[current_year] = (salary_format + ' {}   | {:+4} %').format(current_sum,
                                                                          currency_to_print.name,
                                                                          percent_change)
        last_year_sum = current_sum

    pprint(result, width=40)


def get_monthly_average_by_years(yearly_stats, currency_to_print):
    result = dict()
    for year, grouped_by_currency in yearly_stats.items():
        for currency, all_stats in grouped_by_currency.items():
            if currency == currency_to_print:
                result[year] = int(all_stats['avg'])
    return result
