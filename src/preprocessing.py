import numpy as np
import pandas as pd

np.random.seed(1)


def build_monthly_trends(demand_trend, no_epochs=20):
    columns_to_keep = ['Month DD Raised', 'SkillList', 'No. of FTE Request Raised']
    demand_trend = demand_trend[columns_to_keep]

    demand_trend = demand_trend.groupby(['Month DD Raised', 'SkillList'])[
        'No. of FTE Request Raised'].sum().reset_index()
    demand_trend["Month DD Raised"] = demand_trend["Month DD Raised"].map(
        {"January": 1, "Febuary": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
         "September": 9,
         "October": 10, "November": 11, "December": 12})
    combinations = demand_trend.groupby(['SkillList'])['No. of FTE Request Raised'].sum().reset_index()
    combinations = combinations[~combinations['No. of FTE Request Raised'].isin([1, 2])].reset_index()

    text_to_num = {}
    num_to_text = {}

    for i in range(combinations.shape[0]):
        text = combinations.loc[i, 'SkillList']
        text_to_num[text] = i
        num_to_text[i] = text

    encodings = np.zeros((12, combinations.shape[0]))
    monthly_counts = np.zeros((12, 1))
    months_with_no_data = []
    for i in range(1, 13, 1):
        month_data = demand_trend[demand_trend['Month DD Raised'] == i].reset_index()
        month_data = month_data[~month_data['No. of FTE Request Raised'].isin([1, 2])].reset_index()
        if month_data.shape[0] == 0:
            encodings[i - 1, :] = np.nan
            monthly_counts[i - 1, 0] = np.nan
            months_with_no_data.append(i)
        else:
            monthly_counts[i - 1, 0] = month_data['No. of FTE Request Raised'].sum()
            for j in range(month_data.shape[0]):
                encodings[i - 1, text_to_num[month_data.loc[j, 'SkillList']]] = month_data.loc[
                    j, 'No. of FTE Request Raised']

    probability_matrix = np.zeros((12, combinations.shape[0]))
    for i in range(probability_matrix.shape[0]):
        if not np.isnan(encodings[i, 0]):
            probability_matrix[i, :] = encodings[i, :] / np.sum(encodings[i, :])

    for month in months_with_no_data:
        month_index = month - 1
        probability_matrix[month_index, :] = (probability_matrix[month_index - 1, :] + probability_matrix[
                                                                                       month_index + 1, :]) / 2
        monthly_counts[month_index, 0] = int((monthly_counts[month_index - 1, 0] + monthly_counts[
            month_index + 1, 0]) / 2)

    probability_range = probability_matrix
    for column in range(1, probability_range.shape[1]):
        probability_range[:, column] = probability_range[:, column - 1] + probability_range[:, column]

    no_of_months = no_epochs * 12
    noise = 0.02
    monthly_trends = np.zeros((no_of_months, probability_range.shape[1]))
    for month_index in range(no_of_months):
        month_probability = probability_range[month_index % 12, :]
        monthly_noise = int(noise * monthly_counts[month_index % 12, 0])
        no_of_jobs = int(
            monthly_counts[month_index % 12, 0] + np.random.randint(low=0, high=monthly_noise))
        for job in range(no_of_jobs):
            prob = np.random.random_sample()
            for i in range(month_probability.shape[0]):
                if prob <= month_probability[i]:
                    monthly_trends[month_index, i] += 1
                    break

    return monthly_trends, (text_to_num, num_to_text)


def split(headcount):
    headcount = headcount[
        ["Status", "SkillList"]]

    billable_resources = headcount[headcount['Status'] == 'Billable']
    bench = headcount[headcount['Status'] == 'Bench']

    return billable_resources[['SkillList']], bench[['SkillList']]


def fill_null(demand_trend):
    demand_trend = demand_trend.sort_values(by=['SkillList', 'Practice'])
    for i in range(demand_trend.shape[0]):
        example = demand_trend.iloc[i, :]
        if pd.notna(example['Skill Group']):
            continue
        else:
            demand_trend.loc[i, 'Skill Group'] = demand_trend.loc[i - 1, 'Skill Group']

    return demand_trend
