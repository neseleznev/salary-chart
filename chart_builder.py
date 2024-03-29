#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
from datetime import date, datetime
from statistics import mode
from typing import List, Any, Dict

import matplotlib as mpl
import matplotlib.pyplot as plt

from core.currency_converter import CurrencySalaryConverter
from core.date_util import month_generator
from core.models import EmploymentPeriod, Salary, Currency
from core.purchasing_power_converter import purchasing_power_converters
from core.salary_calculator.salary_calculator import SalaryCalculator
from core.yearly_calculator.yearly_stats import print_yearly_stats

OUT_PUT_DPI = 400
OUTPUT_FORMAT = 'svg'  # 'png' is also supported

# TITLE = 'Your relative salary'
TITLE = 'Относительная з/п'
# X_AXIS_LABEL = 'Month'
X_AXIS_LABEL = 'Месяц'

# MAIN_CURRENCY_SALARY_LABEL = 'Main currency salary'
MAIN_CURRENCY_SALARY_LABEL = 'З/п в основной валюте'
MAIN_CURRENCY_COLOR = '#303F9F'  # 'tab:blue'

# VALUE_CHANGE_LABEL = 'Salary with value change since first employment'
VALUE_CHANGE_LABEL = 'З/п с учётом покупательной способности (с момента первого трудоустройства)'
LATEST_VALUE_CHANGE_DATA_LABEL = 'Дата последних данных о покупательной способности'
VALUE_CHANGE_COLOR = '#D32F2F'  # 'darkred'
LATEST_VALUE_CHANGE_COLOR = '#757575'  # 'grey'

# USD_SALARY_LABEL = 'USD salary'
USD_SALARY_LABEL = 'Зарплата в USD'
USD_COLOR = '#4CAF50'  # 'darkgreen'

ENABLE_INCREASE_DECREASE_CARETS = False

# INCREASE_LABEL = 'Increase'
INCREASE_LABEL = 'Повышение'
INCREASE_COLOR = '#037149'

# DECREASE_LABEL = 'Decrease'
DECREASE_LABEL = 'Понижение'
DECREASE_COLOR = '#be0000'

YEAR_MONTH_FMT = '%Y-%m'
AMOUNT_LABEL_SHIFT_RATIO = 0.05


class GraphData:
    def __init__(self, salary: Dict[str, int]):
        self._salary = {key: value for key, value in salary.items() if value is not None}

    @property
    def months(self):
        return list(self._salary.keys())

    @property
    def amounts(self):
        return list(self._salary.values())


class EmploymentData:
    def __init__(self, periods: List[EmploymentPeriod], salary_calculator: SalaryCalculator):
        self._periods = periods
        self._salary_calculator = salary_calculator

        self._months = []
        self._init_months()

    @property
    def months(self):
        return self._months.copy()

    def salaries(self, new_currency: Currency) -> GraphData:
        return GraphData(self._salaries(new_currency))

    def _salaries(self, new_currency: Currency) -> Dict[str, int]:
        salary = self._salary_calculator.convert(self._periods, [new_currency], [])

        return {dt: converted[new_currency] for dt, converted in salary.salaries.items()}

    def value_change(self) -> GraphData:
        salary = self._salary_calculator.convert(self._periods, [], [Currency.RUB])
        return GraphData({dt: converted[Currency.RUB] for dt, converted in salary.salaries_purchasing_power.items()})

    @property
    def most_frequent_currency(self) -> Currency:
        return mode([x.salary.currency for x in self._periods])

    def _init_months(self):
        begin = self._begin_date()
        end = self._end_date()
        for month in month_generator(begin, end):
            self._months.append(month)

    def _begin_date(self):
        return min(p.begin for p in self._periods)

    def _end_date(self):
        return max(p.end for p in self._periods)


def filter_by_indices(values: List[Any], indices: List[int]):
    return [val for idx, val in enumerate(values) if idx in indices]


def build_graph(salary_data: List[EmploymentPeriod],
                main_currency: Currency):
    # plt.figure(figsize=(16, 10), dpi=80)

    fig, y_axis1 = plt.subplots()
    fig.set_dpi(OUT_PUT_DPI)
    fig.set_figwidth(12)
    fig.set_figheight(8)

    calculator = SalaryCalculator(CurrencySalaryConverter(), purchasing_power_converters)
    data = EmploymentData(salary_data, calculator)

    plt.title(TITLE, fontsize=22)
    y_axis1.set_xlabel(X_AXIS_LABEL)

    fig.autofmt_xdate()

    draw_main_currency_line(data, main_currency, y_axis1)
    draw_value_change_line(data, y_axis1)

    # instantiate a second axes that shares the same x-axis
    y_axis2 = y_axis1.twinx()

    # Reorder sub-axis: main currency graph on top
    y_axis1.zorder = 2
    y_axis2.zorder = 1
    y_axis1.patch.set_visible(False)  # hide the 'canvas'

    y_axis1.grid(True)
    y_axis2.grid(True)

    draw_usd_line(data, y_axis2)

    add_legends(y_axis1, y_axis2)
    stylize_plot()
    plt.savefig('salary.%s' % OUTPUT_FORMAT)
    plt.show()


def draw_main_currency_line(data: EmploymentData, main_currency: Currency, axis):
    main_data = data.salaries(main_currency)

    axis.set_ylabel(main_currency.name, color=MAIN_CURRENCY_COLOR)
    axis.tick_params(axis='y', labelcolor=MAIN_CURRENCY_COLOR)

    axis.step(main_data.months, main_data.amounts,
              color=MAIN_CURRENCY_COLOR,
              label=f'{MAIN_CURRENCY_SALARY_LABEL} ({main_currency.name})')

    if ENABLE_INCREASE_DECREASE_CARETS:
        draw_increase_carets(main_data, axis, 10)
        draw_decrease_carets(main_data, axis, 10)


def draw_value_change_line(data: EmploymentData, axis):
    data = data.value_change()

    axis.step(data.months, data.amounts,
              color=VALUE_CHANGE_COLOR,
              label=VALUE_CHANGE_LABEL)
    plt.axvline(data.months[-1], 0, 1, label=LATEST_VALUE_CHANGE_DATA_LABEL, c=LATEST_VALUE_CHANGE_COLOR)


def draw_usd_line(data: EmploymentData, axis):
    main_data = data.salaries(Currency.USD)

    axis.set_ylabel(Currency.USD.name, color=USD_COLOR)
    axis.tick_params(axis='y', labelcolor=USD_COLOR)

    axis.step(main_data.months, main_data.amounts,
              color=USD_COLOR,
              label=USD_SALARY_LABEL, alpha=1.0)


def draw_increase_carets(data: GraphData, axis, max_count: int = None):
    draw_change_carets(data, axis, 1, mpl.markers.CARETUPBASE, INCREASE_COLOR,
                       INCREASE_LABEL, INCREASE_COLOR, max_count)


def draw_decrease_carets(data: GraphData, axis, max_count: int = None):
    draw_change_carets(data, axis, -1, mpl.markers.CARETDOWNBASE, DECREASE_COLOR,
                       DECREASE_LABEL, DECREASE_COLOR, max_count)


def draw_change_carets(data: GraphData, axis,
                       diff_sign: int, marker, color: str,
                       label: str, caret_color: str, max_count: int = None):
    change_locations = get_change_locations(data.amounts, diff_sign)

    if max_count:
        filter_uniformly(change_locations, max_count)

    axis.scatter(filter_by_indices(data.months, change_locations),
                 filter_by_indices(data.amounts, change_locations),
                 marker=marker, color=color, s=100, label=label)

    amount_range = abs(max(data.amounts) - min(data.amounts))
    amount_label_shift = diff_sign * amount_range * AMOUNT_LABEL_SHIFT_RATIO

    for t in change_locations:
        axis.text(data.months[t], data.amounts[t] + amount_label_shift,
                  data.months[t].strftime(YEAR_MONTH_FMT),
                  horizontalalignment='center',
                  color='white',
                  bbox=dict(facecolor=color, alpha=0.75))


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


def add_legends(axis1, axis2):
    axis1.legend(loc='upper left')
    axis2.legend(loc='lower right')


def stylize_plot():
    # Lighten borders
    plt.gca().spines["top"].set_alpha(.0)
    plt.gca().spines["bottom"].set_alpha(.3)
    plt.gca().spines["right"].set_alpha(.0)
    plt.gca().spines["left"].set_alpha(.3)

    plt.grid(axis='y', alpha=.3, color=USD_COLOR)


if __name__ == '__main__':
    periods: List[EmploymentPeriod] = [
        EmploymentPeriod('Zavod, LLC', date(2014, 3, 1), date(2016, 3, 31), Salary(40000, Currency.RUB)),
        EmploymentPeriod('Zavod, LLC', date(2016, 4, 1), date(2018, 3, 31), Salary(50000, Currency.RUB)),
        EmploymentPeriod('Zavod, LLC', date(2018, 4, 1), datetime.now().date(), Salary(60000, Currency.RUB)),
    ]

    print_yearly_stats(periods, [Currency.USD, Currency.EUR, Currency.RUB])
    build_graph(periods, Currency.RUB)
