import json
import os
import random
from datetime import datetime


def write_data_into_file(file_path, data, mode):
    with open(file_path, mode) as file:
        file.write(data)
    file.close()

def get_cost(consumption, rate):
    cost = (consumption / rate).__round__(2)
    return cost

def get_bc_duration(bc_start, bc_end,is_end_date_inclusive):
    if is_end_date_inclusive:
        print()
        bc_duration = str((datetime.strptime(bc_end, "%Y-%m-%d") - datetime.strptime(bc_start, "%Y-%m-%d")).days+1)
    else:
        bc_duration = str((datetime.strptime(bc_end, "%Y-%m-%d") - datetime.strptime(bc_start, "%Y-%m-%d")).days)
    return bc_duration

def populate_billing_data_cost_consumption_values(record, cost, consumption, bc_start, bc_end, bc_duration):
    record = record.replace('{' + "consumption" + '}', str(consumption))
    record = record.replace('{' + "cost" + '}', str(cost))
    record = record.replace('{' + "bc_start" + '}', bc_start)
    record = record.replace('{' + "bc_end" + '}', bc_end)
    record = record.replace('{' + "bc_duration" + '}', bc_duration)
    return record

def get_random_consumption_data(start, end):
    usage = random.uniform(start, end).__round__(2)
    return usage

def get_absolute_file_path_from_relative_path(relative_path):
    absolute_path = os.path.abspath(relative_path)
    return absolute_path

def populate_variable_fields_with_static_key(record, variable_fields_with_static_key, id):
    for variable_column_field in variable_fields_with_static_key:
        value = variable_fields_with_static_key[variable_column_field]
        if id != -1:
            value = value + "_" + str(id)
        record = record.replace('{' + variable_column_field + '}', value)

    return record

def get_configs_from_config_file(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    return data

def write_list_into_file(list_data, file_path, mode):
    data = ""
    for values in list_data:
        data = data + values + "\n"

    write_data_into_file(file_path, data, mode)


def create_user_enrollment_record(user_configs):
    dummy_user_record = user_configs["dummy_user_record"]
    variable_fields_with_static_key = user_configs["variable_fields_with_static_key"]
    users_to_be_created = user_configs["users_to_be_created"]
    file_path = user_configs["user_enrollment_file_path"]
    user_id_start = user_configs["user_id_start"]

    user_enrollment_list = []
    for id in range(user_id_start, user_id_start + users_to_be_created):
        user_record = populate_variable_fields_with_static_key(dummy_user_record, variable_fields_with_static_key, id)
        user_enrollment_list.append(user_record)

    file_write_mode = "a"
    write_list_into_file(user_enrollment_list, file_path, file_write_mode)

def create_billing_data_for_a_user(billing_data_configs, billing_cycle_list, rate, id):
    file_write_mode = "a"

    billing_data_file_path = billing_data_configs["billing_data_file_path"]
    dummy_billing_data_record = billing_data_configs["dummy_billing_data_record"]
    variable_fields_with_static_key = billing_data_configs["variable_fields_with_static_key"]
    is_billing_end_date_inclusive = billing_data_configs["is_billing_end_date_inclusive"]

    consumption_range_start=billing_data_configs["consumption_range_start"]
    consumption_range_end = billing_data_configs["consumption_range_end"]

    user_billing_data_record = []

    billing_data_record = populate_variable_fields_with_static_key(dummy_billing_data_record,
                                                                   variable_fields_with_static_key, id)

    for bill_cycle in billing_cycle_list:
        bc_start = bill_cycle["start"]
        bc_end = bill_cycle["end"]

        bc_duration = get_bc_duration(bc_start, bc_end,is_billing_end_date_inclusive)

        consumption = get_random_consumption_data(consumption_range_start,consumption_range_end)

        cost = get_cost(consumption, rate)

        single_billing_data_record = populate_billing_data_cost_consumption_values(billing_data_record, cost,
                                                                                   consumption, bc_start, bc_end,
                                                                                   bc_duration)

        user_billing_data_record.append(single_billing_data_record)

    write_list_into_file(user_billing_data_record, billing_data_file_path, file_write_mode)

if __name__=='__main__':
    print("welcome :)")

    config_file_path = get_absolute_file_path_from_relative_path("nwn_config.json")
    configs = get_configs_from_config_file(config_file_path)
    user_configs = configs["user_enrollment"]

    need_to_create_users = configs["user_inputs"]["create_user_enrollment"]
    need_to_create_billing_data_for_user = configs["user_inputs"]["create_billing_data"]

    if need_to_create_users:
        print("creating user enrollment records...")
        create_user_enrollment_record(user_configs)
        print("created user enrollment records!")

    if need_to_create_billing_data_for_user:
        user_id_start = user_configs["user_id_start"]
        unique_users_count = configs["user_enrollment"]["users_to_be_created"]
        print("creating billing data file...")
        for id in range(user_id_start, user_id_start + unique_users_count):
            billing_data_configs = configs["billing_data"]
            rate = configs["user_inputs"]["default_rate"]
            billing_cycles=configs["bc_schedule"]["billing_cycles"]
            create_billing_data_for_a_user(billing_data_configs, billing_cycles,rate,id)
        print("created billing data files!")

    print("Done :)")