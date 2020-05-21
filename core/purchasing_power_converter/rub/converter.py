from datetime import date
from typing import List

from .data import get_value_changes, update_stats
from ..base import BasePurchasingPowerSalaryConverter


class RubPurchasingPowerSalaryConverter(BasePurchasingPowerSalaryConverter):

    def __init__(self):
        update_stats()

    def get_purchasing_power_change(self, base_month: date, future_month: date) -> List[int]:
        return get_value_changes(base_month, future_month)
