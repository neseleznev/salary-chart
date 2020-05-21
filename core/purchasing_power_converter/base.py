from datetime import date
from typing import Dict, List


class BasePurchasingPowerSalaryConverter:

    def convert(self, salary: Dict[date, int]) -> Dict[date, int]:
        start_month = min(salary.keys()).replace(day=1)
        end_month = max(salary.keys()).replace(day=1)
        changes = self.get_purchasing_power_change(start_month, end_month)

        result: Dict[date, int] = dict()

        for idx, (month, amount) in enumerate(sorted(salary.items())):
            try:
                value_change = changes[idx]
                result[month] = amount * value_change
            except (IndexError, TypeError):
                result[month] = None  # No more data, return truthy None

        return result

    def get_purchasing_power_change(self, base_month: date, future_month: date) -> List[int]:
        raise NotImplemented("")
