import matplotlib.pyplot as plt
import numpy as np

def analyse(details, revenue_per_billable_r, cost_per_r):
    number_of_billable_res = details['Number of billable resources']
    number_of_benched_res = details['Number of benched resources']
    total_revenue_generated = number_of_billable_res * revenue_per_billable_r
    total_cost = (number_of_billable_res + number_of_benched_res) * cost_per_r
    bench_cost = number_of_benched_res * cost_per_r
    new_possible_business = details['Number of demanded resources'] * revenue_per_billable_r
    new_captured_business = details['Number of demanded resources - fulfilled'] * revenue_per_billable_r
    new_lost_business = new_possible_business - new_captured_business
    old_possible_business = details['Number of resignations (billable resources)'] * revenue_per_billable_r
    old_captured_business = details['Number of resignations (billable resources) - replaced'] * revenue_per_billable_r
    old_lost_business = old_possible_business - old_captured_business

    analysis = {}
    analysis['Total Revenue Generated'] = total_revenue_generated
    analysis['Total Cost'] = total_cost
    analysis['Total Profits'] = total_revenue_generated - total_cost
    analysis['Bench Budget Consumption'] = bench_cost
    analysis['Total Possible Business Value (attrition and demand)'] = new_possible_business + old_possible_business
    analysis['Total Captured Business Value (attrition and demand)'] = new_captured_business + old_captured_business
    analysis['Total Lost Business Value (attrition and demand)'] = new_lost_business + old_lost_business
    analysis['Possible Business Value (through new demand)'] = new_possible_business
    analysis['Captured Business Value (through new demand)'] = new_captured_business
    analysis['Lost Business Value (through new demand)'] = new_lost_business
    analysis['Possible Business Value (replacing resignations)'] = old_possible_business
    analysis['Captured Business Value (replacing resignations)'] = old_captured_business
    analysis['Lost Business Value (replacing resignations)'] = old_lost_business

    return analysis


def analyse_year(year_analysis):
    last_10_months = year_analysis[year_analysis['Month'] > 2]
    last_10_months = last_10_months[
        ['Total Revenue Generated', 'Total Cost', 'Total Profits', 'Bench Budget Consumption',
         'Total Possible Business Value (attrition and demand)',
         'Total Captured Business Value (attrition and demand)',
         'Total Lost Business Value (attrition and demand)',
         'Possible Business Value (through new demand)',
         'Captured Business Value (through new demand)',
         'Lost Business Value (through new demand)',
         'Possible Business Value (replacing resignations)',
         'Captured Business Value (replacing resignations)',
         'Lost Business Value (replacing resignations)']].mean()

    plt.figure()
    plt.bar(np.arange(1, 13), year_analysis["Bench Budget Consumption"])
    plt.xticks(np.arange(1, 13), [str(i) for i in range(1, 13)])
    plt.xlabel("Months")
    plt.ylabel("Bench Budget Consumption")
    plt.title("Monthly Bench Budget Consumption")
    plt.savefig("../results/Bench Budget Consumption.png")

    plt.figure()
    plt.bar(np.arange(1, 13), year_analysis["Total Profits"])
    plt.xticks(np.arange(1, 13), [str(i) for i in range(1, 13)])
    plt.xlabel("Months")
    plt.ylabel("Profits")
    plt.title("Monthly Profits")
    plt.savefig("../results/Total Profits.png")

    plt.figure()
    plt.plot(year_analysis["Total Possible Business Value (attrition and demand)"], color='b')
    plt.plot(year_analysis["Total Captured Business Value (attrition and demand)"], color='r')
    plt.xticks(np.arange(0, 12), [str(i) for i in range(1, 13)])
    plt.xlabel("Months")
    plt.ylabel("Business Value")
    plt.title("Possible vs Captured Business Value")
    plt.savefig("../results/PossibleVCaptured.png")

    year_analysis = year_analysis[['Total Revenue Generated', 'Total Cost', 'Total Profits', 'Bench Budget Consumption',
                                   'Total Possible Business Value (attrition and demand)',
                                   'Total Captured Business Value (attrition and demand)',
                                   'Total Lost Business Value (attrition and demand)',
                                   'Possible Business Value (through new demand)',
                                   'Captured Business Value (through new demand)',
                                   'Lost Business Value (through new demand)',
                                   'Possible Business Value (replacing resignations)',
                                   'Captured Business Value (replacing resignations)',
                                   'Lost Business Value (replacing resignations)']].mean()

    perc_total_captured = (year_analysis['Total Captured Business Value (attrition and demand)'] / year_analysis[
        'Total Possible Business Value (attrition and demand)']) * 100
    perc_demand_captured = (year_analysis['Captured Business Value (through new demand)'] / year_analysis[
        'Possible Business Value (through new demand)']) * 100
    perc_attrition_captured = (year_analysis['Captured Business Value (replacing resignations)'] / year_analysis[
        'Possible Business Value (replacing resignations)']) * 100
    perc_total_captured_10 = (last_10_months['Total Captured Business Value (attrition and demand)'] / last_10_months[
        'Total Possible Business Value (attrition and demand)']) * 100
    perc_demand_captured_10 = (last_10_months['Captured Business Value (through new demand)'] / last_10_months[
        'Possible Business Value (through new demand)']) * 100
    perc_attrition_captured_10 = (last_10_months['Captured Business Value (replacing resignations)'] / last_10_months[
        'Possible Business Value (replacing resignations)']) * 100
    profit = year_analysis['Total Profits'] * 12
    profit_per_dollar_spent = year_analysis['Total Profits'] / year_analysis['Total Cost']
    bench_budget_consumption = year_analysis['Bench Budget Consumption'] * 12

    analysis = {}
    analysis['Percentage of Total Business Captured (attrition and demand) JAN - DEC'] = perc_total_captured
    analysis['Percentage of Total Business Captured (attrition) JAN - DEC'] = perc_attrition_captured
    analysis['Percentage of Total Business Captured (demand) JAN - DEC'] = perc_demand_captured
    analysis['Percentage of Total Business Captured (attrition and demand) MAR - DEC'] = perc_total_captured_10
    analysis['Percentage of Total Business Captured (attrition) MAR - DEC'] = perc_attrition_captured_10
    analysis['Percentage of Total Business Captured (demand) MAR - DEC'] = perc_demand_captured_10
    analysis['Total Profits'] = profit
    analysis['Profit Per Dollar Spent'] = profit_per_dollar_spent
    analysis['Total Bench Budget Consumption'] = bench_budget_consumption

    return analysis
