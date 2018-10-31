import pandas as pd


def plan_supply(forecasted_demand, demand, billable_resources, bench, current_resigning, future_resigning, new_hires,
                utils, max_r):
    # Finding the skill lists of the employees resigning over the next 2 months
    resigning_employees_billable = []
    resigning_employees_bench = []

    # Appending the skill lists of the employees leaving in the current month
    resigning_employees_billable.append(current_resigning[0])
    resigning_employees_bench.append(current_resigning[1])

    # Appending the skill lists of the employees leaving in the next 2 months
    for resigning_batch in future_resigning[:2]:
        resigning_employees_billable.append(resigning_batch[0])
        resigning_employees_bench.append(resigning_batch[1])

    # Concatenating all the skill lists into a single dataframe
    resigning_employees_billable = pd.concat(resigning_employees_billable, axis=0)
    resigning_employees_bench = pd.concat(resigning_employees_bench, axis=0)

    # Calculating currently available employees
    curr_billable = remove(billable_resources, current_resigning[0])
    curr_bench = remove(bench, current_resigning[1])

    if curr_bench.shape[0] + curr_billable.shape[0] + new_hires.shape[0] > max_r:
        no_of_new_hires = max_r - (curr_bench.shape[0] + curr_billable.shape[0])
    else:
        no_of_new_hires = new_hires.shape[0]

    # Adding the new hires to the bench
    curr_bench = pd.concat([curr_bench, new_hires.iloc[:no_of_new_hires, :]], axis=0)

    # Replacing the employees leaving currently
    repl_res_billable, unrepl_res_billable, curr_bench = replace_current_resigning(current_resigning[0], curr_bench)
    no_of_resignations = current_resigning[0].shape[0]
    no_of_replaced_resignations = repl_res_billable.shape[0]
    no_of_unreplaced_resignations = unrepl_res_billable.shape[0]

    no_of_resignations_bench = current_resigning[1].shape[0]

    # Tools for convertion from index to skill list
    text_to_num, num_to_text = utils

    # Mapping indices to skill lists
    current_demand_skilllists = map_skillsets(demand, num_to_text)
    forecasted_demand_skilllists = map_skillsets(forecasted_demand, num_to_text)

    # Assigning jobs according to the demand
    curr_ass_dem, curr_unass_dem, curr_bench = assign_current_jobs(current_demand_skilllists, curr_bench)
    no_of_res_demanded = current_demand_skilllists.shape[0]
    no_of_res_provided = curr_ass_dem.shape[0]
    no_of_res_missed = curr_unass_dem.shape[0]
    curr_billable = pd.concat([curr_billable, repl_res_billable, curr_ass_dem], axis=0)
    no_of_billable_res = curr_billable.shape[0]
    no_of_benched_res = curr_bench.shape[0]

    # Calculating available employees on bench in 2 months
    future_bench = remove(curr_bench, resigning_employees_bench)

    # Planning for the future
    to_hire = plan_future(forecasted_demand_skilllists, future_resigning[1][0], future_bench)
    no_of_planned_hires = to_hire.shape[0]

    details = {}
    details['Headcount'] = no_of_billable_res + no_of_benched_res
    details['Number of billable resources'] = no_of_billable_res
    details['Number of benched resources'] = no_of_benched_res
    details['Number of new hires'] = no_of_new_hires
    details['Number of demanded resources'] = no_of_res_demanded
    details['Number of demanded resources - fulfilled'] = no_of_res_provided
    details['Number of demanded resources - unfulfilled'] = no_of_res_missed
    details['Number of resignations (billable resources)'] = no_of_resignations
    details['Number of resignations (benched resources)'] = no_of_resignations_bench
    details['Number of resignations (billable resources) - replaced'] = no_of_replaced_resignations
    details['Number of planned hires'] = no_of_planned_hires

    return details, curr_billable, curr_bench, to_hire


def remove(df1, df2):
    df1_list = [tuple(line) for line in df1.values]
    df2_list = [tuple(line) for line in df2.values]
    remaining = []
    for employee in df1_list:
        if employee in df2_list:
            df2_list.remove(employee)
        else:
            remaining.append(employee)

    return pd.DataFrame(remaining, columns=list(df1.columns))


def map_skillsets(demand, num_to_text):
    skillsets = pd.DataFrame(columns=['SkillList'])
    for i in range(demand.shape[0]):
        for j in range(int(demand[i])):
            skillsets = skillsets.append({'SkillList': num_to_text[i]}, ignore_index=True)

    return skillsets


def replace_current_resigning(current_resigning_billable, bench):
    unreplaced_resigning_billable = remove(current_resigning_billable, bench)
    replaced_resigning_billable = remove(current_resigning_billable, unreplaced_resigning_billable)
    remaining_bench = remove(bench, replaced_resigning_billable)

    return replaced_resigning_billable, unreplaced_resigning_billable, remaining_bench


def assign_current_jobs(demand, available_employees_bench):
    unassigned_demand = remove(demand, available_employees_bench)
    assigned_demand = remove(demand, unassigned_demand)
    bench = remove(available_employees_bench, assigned_demand)

    return assigned_demand, unassigned_demand, bench


def plan_future(forecasted_demand, resigning_in_2_months, available_future_bench):
    unrep_res_2_months = remove(resigning_in_2_months, available_future_bench)
    rep_res_2_months = remove(resigning_in_2_months, unrep_res_2_months)
    available_future_bench = remove(available_future_bench, rep_res_2_months)
    unass_demand = remove(forecasted_demand, available_future_bench)

    return pd.concat([unrep_res_2_months, unass_demand], axis=0)
