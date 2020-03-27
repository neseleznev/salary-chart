import datetime
import pickle
from itertools import tee
from pprint import pprint

import requests

from date_util import month_generator, add_months

ROOT_URL = 'https://www.statbureau.org/'
HEADERS = {
    'Content-Type': 'application/json; charset=utf-8'
}
DATE_FMT = '%Y/%m/%dZ'
VALUE_AMOUNT = 1_000_000

PICKLE_NAME = 'value_change_to_next_month.pickle'


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


def retrieve_and_dump_stats_to_file(months_step: int):
    month_to_change = dict()

    first_month, last_month = get_available_months()

    for start_month, next_month in pairwise(month_generator(first_month, last_month, months_step)):
        print(start_month)
        print(next_month)
        change = get_value_change(start_month, next_month)
        print(change)
        print()

        for month in month_generator(start_month, next_month, 1):
            month_to_change[month] = change ** (1 / months_step)

    pprint(month_to_change)

    with open(PICKLE_NAME, 'wb') as f:
        pickle.dump(month_to_change, f)


def load_from_file():
    with open(PICKLE_NAME, 'rb') as f:
        month_to_change = pickle.load(f)
    return month_to_change


def get_value_changes(start_month: datetime.date, end_month: datetime.date):
    month_to_change = load_from_file()

    latest_month = min(max(month_to_change.keys()), end_month)

    changes = [1]
    replace = start_month.replace(day=1)
    for month in month_generator(replace, latest_month):
        change = month_to_change.get(month, 1)
        changes.append(changes[-1] * change)
    return changes


if __name__ == '__main__':
    retrieve_and_dump_stats_to_file(1)

    # coefficients = get_value_changes(datetime.date(2016, 1, 17), datetime.date(2019, 5, 25))

    # pprint(coefficients)
