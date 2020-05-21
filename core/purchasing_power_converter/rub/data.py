import datetime
import json
from itertools import tee
from pprint import pprint
from typing import Dict

import requests

from core.date_util import month_generator, add_months

ROOT_URL = 'https://www.statbureau.org/'
HEADERS = {
    'Content-Type': 'application/json; charset=utf-8'
}
DATE_FMT = '%Y/%m/%dZ'
VALUE_AMOUNT = 1_000_000

JSON_NAME = 'core/purchasing_power_converter/rub/purchasing_power_change_to_next_month_step_%d.json'
JSON_DATE_FMT = '%Y-%m-%d'


def get_available_months():
    r = requests.post(ROOT_URL + 'get-data-json',
                      json={
                          'country': 'russia'
                      },
                      headers=HEADERS)
    dates = list(map(data_entry_to_date, r.json()))
    return min(dates), max(dates)


def data_entry_to_date(data_entry):
    unix_time = int(data_entry['Month'][6:-2]) / 1000
    dt = datetime.datetime.fromtimestamp(unix_time) \
        .astimezone(datetime.timezone.utc) \
        .date()
    return dt


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def get_value_change(start_month: datetime.date, end_month: datetime.date):
    r = requests.post(ROOT_URL + 'calculate-inflation-value-json',
                      json={
                          'country': 'russia',
                          'start': start_month.strftime(DATE_FMT),
                          'end': add_months(end_month, -1).strftime(DATE_FMT),
                          'amount': str(VALUE_AMOUNT),
                          'denominationsToApply': '1998-1-1'
                      },
                      headers=HEADERS)
    change = float(r.json()[:-2].replace(' ', '')) / VALUE_AMOUNT
    return change


def update_stats(months_step: int = 1):
    print('Updating purchasing power statistics database...')

    month_to_change = load_from_file(months_step)
    last_saved_data_month = max(month_to_change.keys()) if month_to_change else None

    first_month, last_month = get_available_months()

    print(f'Latest saved date: {last_saved_data_month}\nLatest available date: {last_month}')
    if not last_saved_data_month or last_saved_data_month < last_month:
        print('Downloading missing data...')

    first_month = max(first_month, last_saved_data_month) if last_saved_data_month else first_month

    for start_month, next_month in pairwise(month_generator(first_month, last_month, months_step)):
        change = get_value_change(start_month, next_month)
        print(f'From {start_month} to {next_month} purchasing power increased in {change:.8f} times')

        for month in month_generator(start_month, next_month, 1):
            month_to_change[month] = change ** (1 / months_step)

    return dump_to_file(month_to_change, months_step)


def load_from_file(months_step: int) -> Dict[datetime.date, float]:
    try:
        with open(JSON_NAME % months_step, 'rb') as f:
            str_to_change = json.load(f) or {}
    except FileNotFoundError:
        str_to_change = {}

    return {datetime.datetime.strptime(k, JSON_DATE_FMT).date(): v for k, v in str_to_change.items()}


def dump_to_file(month_to_change: Dict[datetime.date, float], months_step: int):
    str_to_change = {k.strftime(JSON_DATE_FMT): v for k, v in month_to_change.items()}

    with open(JSON_NAME % months_step, 'w') as f:
        json.dump(str_to_change, f, sort_keys=True, indent=4, separators=(',', ': '))
    return str_to_change


def get_value_changes(start_month: datetime.date, end_month: datetime.date, months_step: int = 1):
    month_to_change = load_from_file(months_step)

    latest_month = min(max(month_to_change.keys()), end_month)

    changes = [1]
    replace = start_month.replace(day=1)
    for month in month_generator(replace, latest_month):
        change = month_to_change.get(month, 1)
        changes.append(changes[-1] * change)
    return changes


if __name__ == '__main__':
    dumped_object = update_stats()

    print('Dumped object:')
    pprint(dumped_object)

    # coefficients = get_value_changes(datetime.date(2016, 1, 17), datetime.date(2019, 5, 25))

    # pprint(coefficients)
