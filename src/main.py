import numpy as np
import pandas as pd
from analysis import analyse, analyse_year
from attrition import AttritionSimulator
from demand_modeling import DemandModel
from preprocessing import split, build_monthly_trends
from supply_planning import plan_supply
import argparse

np.random.seed(1)

pd.set_option('display.max_columns', None)

headcount = pd.read_excel("../res/Demandv1.1.xlsx", 'Headcount')

demand_trend = pd.read_excel("../res/Demandv1.1.xlsx", 'Demand Trend Last year')

monthly_demand_trends, utils = build_monthly_trends(demand_trend)

billable, bench = split(headcount)
employees = (billable, bench)

revenue_per_billable_r = 900
cost_per_r = 685
total_bench_budget = 5760000
attrition = 0.2
max_r = 12000
notice_period = 2

parser = argparse.ArgumentParser()
parser.add_argument('-br', '--billable_revenue', help='Revenue that a billable employee brings to the companypytho', required=False)
parser.add_argument('-c', '--cost_per_resource', help='Cost per resource', required=False)
parser.add_argument('-a', '--attrition', help='Probabilty of a person leaving the company', required=False)
parser.add_argument('-ms', '--maximum_strength', help='Maximum number of employees allowed', required=False)

args = parser.parse_args()

print(args.billable_revenue)
print(args.cost_per_resource)

if args.billable_revenue is not None:
    revenue_per_billable_r = float(args.billable_revenue)
if args.cost_per_resource is not None:
    cost_per_r = float(args.cost_per_resource)
if args.attrition is not None:
    attrition = float(args.attrition)
if args.maximum_strength is not None:
    max_r = float(args.maximum_strength)

print("-" * 60)
print("Given Variables")
print("-" * 15)
print("Revenue per billable resource:", revenue_per_billable_r)
print("Cost per resource:", cost_per_r)
print("Total bench budget:", total_bench_budget)
print("Attrition percentage:", attrition * 100)
print("Maximum resources:", max_r)
print("-" * 60)
print()

print("-" * 60)
print("Number of billable resources at the start of the year:", billable.shape[0])
print("Number of resources on the bench at the start of the year:", bench.shape[0])
print("-" * 60)
print()

demand_model = DemandModel(monthly_demand_trends, prev_months=3, verbose=False)
attrition_model = AttritionSimulator(employees=employees, attrition=attrition, notice_period=notice_period)

demand_seen = np.zeros((12, monthly_demand_trends.shape[1]))

new_hires = {}

year_details = pd.DataFrame(
    columns=['Month', 'Headcount', 'Number of billable resources', 'Number of benched resources', 'Number of new hires',
             'Number of demanded resources', 'Number of demanded resources - fulfilled',
             'Number of demanded resources - unfulfilled', 'Number of resignations (billable resources)',
             'Number of resignations (benched resources)',
             'Number of resignations (billable resources) - replaced', 'Number of planned hires'])
year_analysis = pd.DataFrame(
    columns=['Month', 'Total Revenue Generated', 'Total Cost', 'Total Profits', 'Bench Budget Consumption',
             'Total Possible Business Value (attrition and demand)',
             'Total Captured Business Value (attrition and demand)', 'Total Lost Business Value (attrition and demand)',
             'Possible Business Value (through new demand)', 'Captured Business Value (through new demand)',
             'Lost Business Value (through new demand)', 'Possible Business Value (replacing resignations)',
             'Captured Business Value (replacing resignations)', 'Lost Business Value (replacing resignations)'])

for month_no in range(1, 13):
    print("-" * 75)
    print("Month", month_no)

    current_resigning = attrition_model.get_resigning_employees(month_no)
    future_resigning = attrition_model.get_future_resigning_employees(month_no)

    current_new_hires = new_hires.get(month_no, pd.DataFrame(columns=['SkillList']))

    demand = demand_model.predict_demand(demand_seen)
    demand_seen[month_no - 1, :] = demand

    forecasted_demand = demand_model.predict_demand_in_2_months(demand_seen)

    details, billable, bench, new_hires[month_no + 2] = plan_supply(forecasted_demand, demand, billable,
                                                                    bench,
                                                                    current_resigning, future_resigning,
                                                                    current_new_hires, utils, max_r)

    current_resigning[0].to_csv("../results/" + str(month_no) + "/Resigning_Billable.csv", index=False)
    current_resigning[1].to_csv("../results/" + str(month_no) + "/Resigning_Bench.csv", index=False)
    billable.to_csv("../results/" + str(month_no) + "/Billable_Resources.csv", index=False)
    bench.to_csv("../results/" + str(month_no) + "/Benched_Resources.csv", index=False)
    new_hires[month_no + 2].to_csv("../results/" + str(month_no) + "/SkillLists_To_Hire.csv", index=False)

    analysis = analyse(details, revenue_per_billable_r, cost_per_r)

    print("-" * 25)
    print("Details")
    for key in details.keys():
        print(key, ":", details[key])

    print("-" * 25)
    print("Analysis")
    for key in analysis.keys():
        print(key, ":", analysis[key])

    details['Month'] = month_no
    analysis['Month'] = month_no

    year_details = year_details.append(details, ignore_index=True)
    year_analysis = year_analysis.append(analysis, ignore_index=True)

    attrition_model.update_employees((billable, bench))

mean_details = year_details[
    ['Headcount', 'Number of billable resources', 'Number of benched resources', 'Number of new hires',
     'Number of demanded resources', 'Number of demanded resources - fulfilled',
     'Number of demanded resources - unfulfilled', 'Number of resignations (billable resources)',
     'Number of resignations (benched resources)',
     'Number of resignations (billable resources) - replaced', 'Number of planned hires']].mean()

analysis = analyse_year(year_analysis)

print("-" * 75)
print("End of Simulation")
print("-" * 25)
print("Final Results")
print("-" * 25)
for key in analysis.keys():
    print(key, ":", analysis[key])

year_details.to_csv("../results/Details - Year.csv", index=False)
year_analysis.to_csv("../results/Analysis - Year.csv", index=False)
