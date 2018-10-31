import numpy as np
import pandas as pd

np.random.seed(1)


class AttritionSimulator:

    def __init__(self, employees, attrition=0.2, notice_period=2):

        self.attrition = attrition
        self.resigning_employees = {}
        self.billable = employees[0]
        self.bench = employees[1]
        self.notice_period = notice_period

        billable = self.billable.copy()
        bench = self.bench.copy()
        for i in range(1, 1 + self.notice_period + 1):
            mask_billable = np.random.rand(billable.shape[0]) < (self.attrition / 12)
            mask_bench = np.random.rand(bench.shape[0]) < (self.attrition / 12)
            billable_resigning = billable[mask_billable]
            bench_resigning = bench[mask_bench]
            billable = billable[~mask_billable]
            bench = bench[~mask_bench]
            self.resigning_employees[i] = (billable_resigning, bench_resigning)

    def get_resigning_employees(self, month_no):

        return self.resigning_employees[month_no]

    def get_future_resigning_employees(self, month_no):
        if month_no == 1:
            future_resigning = []
            for month in range(month_no + 1, month_no + self.notice_period + 1):
                future_resigning.append(self.resigning_employees[month])

            return future_resigning
        else:
            billable = self.billable.copy()
            bench = self.bench.copy()

            for month in range(month_no, month_no + self.notice_period):
                (billable_resigning, bench_resigning) = self.get_resigning_employees(month)

                billable = self._remove_employees(billable, billable_resigning)
                bench = self._remove_employees(bench, bench_resigning)

            mask_billable = np.random.rand(billable.shape[0]) < (self.attrition / 12)
            mask_bench = np.random.rand(bench.shape[0]) < (self.attrition / 12)
            billable_resigning = billable[mask_billable]
            bench_resigning = bench[mask_bench]
            self.resigning_employees[month_no + self.notice_period] = (billable_resigning, bench_resigning)

            future_resigning = []
            for month in range(month_no + 1, month_no + self.notice_period + 1):
                future_resigning.append(self.resigning_employees[month])

            return future_resigning

    @staticmethod
    def _remove_employees(all, resigning):

        all_list = [tuple(line) for line in all.values]
        resigning_list = [tuple(line) for line in resigning.values]
        remaining = []
        for employee in all_list:
            if employee in resigning_list:
                resigning_list.remove(employee)
            else:
                remaining.append(employee)

        return pd.DataFrame(remaining, columns=list(all.columns))

    def update_employees(self, employees):

        self.billable = employees[0]
        self.bench = employees[1]
