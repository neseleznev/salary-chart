from datetime import date
from enum import Enum
from typing import Union


class Currency(Enum):
    """
    ISO 4217 currency codes
    """
    RUB = 'RUB'
    USD = 'USD'

    BRL = 'BRL'
    PHP = 'PHP'
    SEK = 'SEK'
    MXN = 'MXN'
    HKD = 'HKD'
    ILS = 'ILS'
    IDR = 'IDR'
    NZD = 'NZD'
    MYR = 'MYR'
    SKK = 'SKK'
    LVL = 'LVL'
    CZK = 'CZK'
    CYP = 'CYP'
    AUD = 'AUD'
    SGD = 'SGD'
    THB = 'THB'
    INR = 'INR'
    GBP = 'GBP'
    MTL = 'MTL'
    EUR = 'EUR'
    ISK = 'ISK'
    PLN = 'PLN'
    HRK = 'HRK'
    KRW = 'KRW'
    RON = 'RON'
    BGN = 'BGN'
    SIT = 'SIT'
    LTL = 'LTL'
    NOK = 'NOK'
    CNY = 'CNY'
    ROL = 'ROL'
    TRY = 'TRY'
    TRL = 'TRL'
    HUF = 'HUF'
    JPY = 'JPY'
    CAD = 'CAD'
    EEK = 'EEK'
    DKK = 'DKK'
    ZAR = 'ZAR'
    CHF = 'CHF'


class Salary:
    def __init__(self, amount: Union[int, float], currency: Currency):
        self.amount = int(amount)
        self.currency = currency


class EmploymentPeriod:
    def __init__(self, company: str, begin: date, end: date, salary: Salary):
        self.company = company
        self.begin = begin
        self.end = end
        self.salary = salary
