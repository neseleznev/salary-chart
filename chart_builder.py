#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import date, timedelta, datetime
from statistics import mode
from typing import List, Any, Callable, Dict

import math
import matplotlib as mpl
import matplotlib.pyplot as plt
from currency_converter import CurrencyConverter, RateNotFoundError

from date_util import month_generator
from download_purchasing_power import get_value_changes

# TITLE = 'Your relative salary'
TITLE = 'Относительная з/п'
# X_AXIS_LABEL = 'Month'
X_AXIS_LABEL = 'Месяц'

# MAIN_CURRENCY_SALARY_LABEL = 'Main currency salary'
MAIN_CURRENCY_SALARY_LABEL = 'З/п в основной валюте'
MAIN_CURRENCY_COLOR = 'tab:blue'

# VALUE_CHANGE_LABEL = 'Salary with value change since first employment'
VALUE_CHANGE_LABEL = 'З/п с учётом покупательной способности (с момента первого трудоустройства)'
VALUE_CHANGE_COLOR = 'darkred'

# USD_SALARY_LABEL = 'USD salary'
USD_SALARY_LABEL = 'Зарплата в USD'
USD_COLOR = 'darkgreen'

# INCREASE_LABEL = 'Increase'
INCREASE_LABEL = 'Повышение'
# DECREASE_LABEL = 'Decrease'
DECREASE_LABEL = 'Понижение'

RUBLES_CODE = 'RUB'
USD_CODE = 'USD'

YEAR_MONTH_FMT = '%Y-%m'
AMOUNT_LABEL_SHIFT_RATIO = 0.05
CURRENCY_RATES_DATA = 'http://www.ecb.int/stats/eurofxref/eurofxref-hist.zip'


class Salary:
    def __init__(self, amount: int, currency_3_letters_code: str):
        # c = CurrencyConverter()
        # c.convert()
        self.amount = amount
        self.currency = currency_3_letters_code  # ISO 4217


class EmploymentPeriod:
    def __init__(self, company: str, begin: date, end: date, salary: Salary):
        self.company = company
        self.begin = begin
        self.end = end
        self.salary = salary


class GraphData:
    def __init__(self, salary: Dict[str, int]):
        self._salary = salary

    @property
    def begin_labels(self):
        return list(self._salary.keys())

    @property
    def amounts(self):
        return list(self._salary.values())


class EmploymentData:
    def __init__(self, periods: List[EmploymentPeriod]):
        self._periods = periods
        self._converter = CurrencyConverter(
            # CURRENCY_RATES_DATA TODO
        )

        self._month_labels = []
        self._init_month_labels()

        self._monthly_salary = dict()
        self._init_monthly_salary()

    @property
    def month_labels(self):
        return self._month_labels.copy()

    def salaries(self, new_currency: str) -> GraphData:
        return GraphData(self._salaries(new_currency))

    def _salaries(self, new_currency: str) -> Dict[str, int]:
        salary = self._monthly_salary.copy()

        for period in self._periods:
            for month in month_generator(period.begin, period.end):
                converted = self._convert(period, new_currency, month)
                salary[month.strftime(YEAR_MONTH_FMT)] += converted

        for key, value in salary.items():
            salary[key] = round(value)
        return salary

    def value_change(self):
        salary = self._salaries(RUBLES_CODE)

        start_month = datetime.strptime(min(salary.keys()), "%Y-%m").replace(day=1).date()
        end_month = datetime.strptime(max(salary.keys()), "%Y-%m").replace(day=1).date()
        changes = get_value_changes(start_month, end_month)

        for idx, (month, amount) in enumerate(sorted(salary.items())):
            try:
                value_change = changes[idx]
            except IndexError:
                value_change = 1  # No more data, don't change the value
            salary[month] = amount * value_change
        return GraphData(salary)

    def most_frequent_currency(self) -> str:
        return mode([x.salary.currency for x in self._periods])

    def _init_monthly_salary(self):
        for month_label in self._month_labels:
            self._monthly_salary[month_label] = 0

    def _init_month_labels(self):
        begin = self._begin_date()
        end = self._end_date()
        for month in month_generator(begin, end):
            self._month_labels.append(month.strftime(YEAR_MONTH_FMT))

    def _begin_date(self):
        return min(p.begin for p in self._periods)

    def _end_date(self):
        return max(p.end for p in self._periods)

    def _convert(self, period: EmploymentPeriod, new_currency: str, dt: date):
        def convert(d: date):
            return self._converter.convert(period.salary.amount,
                                           period.salary.currency,
                                           new_currency,
                                           d)

        try:
            return convert(dt)
        except RateNotFoundError:
            return EmploymentData._convert_in_neighbour_dates(convert, dt)

    @staticmethod
    def _convert_in_neighbour_dates(convert: Callable, dt: date):
        latest_exception = None

        for days in range(1, 100):
            for sign in (1, -1):
                try:
                    return convert(dt + timedelta(days * sign))
                except RateNotFoundError as ex:
                    latest_exception = ex
                    continue
        raise latest_exception


def filter_by_indices(values: List[Any], indices: List[int]):
    return [val for idx, val in enumerate(values) if idx in indices]


def format_labels(dates: List[date]) -> List[str]:
    return [d.strftime(YEAR_MONTH_FMT) for d in dates]


def build_graph(salary_data: List[EmploymentPeriod]):
    # plt.figure(figsize=(16, 10), dpi=80)

    fig, y_axis1 = plt.subplots()
    fig.set_dpi(100)
    fig.set_figwidth(12)
    fig.set_figheight(8)

    data = EmploymentData(salary_data)

    plt.title(TITLE, fontsize=22)
    y_axis1.set_xlabel(X_AXIS_LABEL)
    stylize_x_ticks(45)

    draw_main_currency_line(data, y_axis1)
    draw_value_change_line(data, y_axis1)

    # instantiate a second axes that shares the same x-axis
    y_axis2 = y_axis1.twinx()
    draw_usd_line(data, y_axis2)

    draw_x_ticks(y_axis1.xaxis, data.month_labels, 20)

    add_legends(y_axis1, y_axis2)
    stylize_plot()
    plt.savefig('salary.png')
    plt.show()


def draw_main_currency_line(data: EmploymentData, axis):
    main_currency = data.most_frequent_currency()
    main_data = data.salaries(main_currency)

    axis.set_ylabel(main_currency, color=MAIN_CURRENCY_COLOR)
    axis.tick_params(axis='y', labelcolor=MAIN_CURRENCY_COLOR)

    axis.step(main_data.begin_labels, main_data.amounts,
              color=MAIN_CURRENCY_COLOR,
              label=f'{MAIN_CURRENCY_SALARY_LABEL} ({main_currency})')

    draw_increase_carets(main_data, axis, 10)
    draw_decrease_carets(main_data, axis, 10)


def draw_value_change_line(data: EmploymentData, axis):
    data = data.value_change()

    axis.step(data.begin_labels, data.amounts,
              color=VALUE_CHANGE_COLOR,
              label=VALUE_CHANGE_LABEL)


def draw_usd_line(data: EmploymentData, axis):
    main_data = data.salaries(USD_CODE)

    axis.set_ylabel(USD_CODE, color=USD_COLOR)
    axis.tick_params(axis='y', labelcolor=USD_COLOR)

    axis.step(main_data.begin_labels, main_data.amounts,
              color=USD_COLOR,
              label=USD_SALARY_LABEL, alpha=0.45)


def draw_increase_carets(data: GraphData, axis, max_count: int = None):
    draw_change_carets(data, axis, 1, mpl.markers.CARETUPBASE, 'tab:green',
                       INCREASE_LABEL, 'darkgreen', max_count)


def draw_decrease_carets(data: GraphData, axis, max_count: int = None):
    draw_change_carets(data, axis, -1, mpl.markers.CARETDOWNBASE, 'tab:red',
                       DECREASE_LABEL, 'darkred', max_count)


def draw_change_carets(data: GraphData, axis,
                       diff_sign: int, marker, color: str,
                       label: str, caret_color: str, max_count: int = None):
    change_locations = get_change_locations(data.amounts, diff_sign)

    if max_count:
        filter_uniformly(change_locations, max_count)

    axis.scatter(filter_by_indices(data.begin_labels, change_locations),
                 filter_by_indices(data.amounts, change_locations),
                 marker=marker, color=color, s=100, label=label)

    amount_range = abs(max(data.amounts) - min(data.amounts))
    amount_label_shift = diff_sign * amount_range * AMOUNT_LABEL_SHIFT_RATIO

    for t in change_locations:
        axis.text(data.begin_labels[t], data.amounts[t] + amount_label_shift,
                  data.begin_labels[t], horizontalalignment='center', color=caret_color)


def get_change_locations(amounts: List[int], diff_sign: int) -> List[int]:
    # import numpy as np
    # np.sign(np.diff(amounts))
    # return np.where(df == diff_sign)[0]
    df = sign(diff(amounts))
    return [idx for idx, x in enumerate(df) if x == diff_sign]


def diff(lst: List) -> List:
    return [lst[i] - lst[i - 1] for i in range(1, len(lst))]


def sign(lst: List) -> List:
    return [1 if x > 0 else (-1 if x < 0 else 0) for x in lst]


def filter_uniformly(lst: list, count: int):
    slice_step = max(1, math.ceil(len(lst) / count))
    return lst[::slice_step]


def stylize_x_ticks(rotation: int = 0):
    plt.xticks(rotation=rotation, fontsize=12, alpha=.7)


def draw_x_ticks(x_axis, date_labels: List[str], max_count: int = None):
    x_tick_location = list(range(len(date_labels)))

    if max_count:
        x_tick_location = filter_uniformly(x_tick_location, max_count)

    x_axis.set_ticks(ticks=x_tick_location)


def add_legends(axis1, axis2):
    axis1.legend(loc='upper left')
    axis2.legend(loc='lower right')


def stylize_plot():
    # plt.ylim(0)
    # plt.yticks(fontsize=12, alpha=.7)

    # Lighten borders
    plt.gca().spines["top"].set_alpha(.0)
    plt.gca().spines["bottom"].set_alpha(.3)
    plt.gca().spines["right"].set_alpha(.0)
    plt.gca().spines["left"].set_alpha(.3)

    plt.grid(axis='y', alpha=.3)


if __name__ == '__main__':
    build_graph([
        EmploymentPeriod('Zavod, LLC', date(2014, 3, 1), date(2016, 3, 31), Salary(40000, 'RUB')),
        EmploymentPeriod('Zavod, LLC', date(2016, 4, 1), date(2018, 3, 31), Salary(50000, 'RUB')),
        EmploymentPeriod('Zavod, LLC', date(2018, 4, 1), date(2019, 5, 31), Salary(60000, 'RUB')),
    ])
