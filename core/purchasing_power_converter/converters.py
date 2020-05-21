from typing import Dict

from .base import BasePurchasingPowerSalaryConverter
from .rub.converter import RubPurchasingPowerSalaryConverter
from ..models import Currency

__all__ = ['purchasing_power_converters']

purchasing_power_converters: Dict[Currency, BasePurchasingPowerSalaryConverter] = {
    Currency.RUB: RubPurchasingPowerSalaryConverter()
}
