import json
import os
import random
import time
from datetime import datetime

import requests


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


def create_meter_enrollment_record(meter_configs, meters_to_be_created, meter_id_start):
    dummy_user_record = meter_configs["dummy_meter_record"]
    variable_fields_with_static_key = meter_configs["variable_fields_with_static_key"]
    file_path = meter_configs["meter_enrollment_file_path"]
    meter_enrollment_list = []
    for id in range(meter_id_start, meter_id_start + meters_to_be_created):
        meter_record = populate_variable_fields_with_static_key(dummy_user_record, variable_fields_with_static_key, id)
        meter_enrollment_list.append(meter_record)

    file_write_mode = "a"
    write_list_into_file(meter_enrollment_list, file_path, file_write_mode)


def get_raw_data_end_timestamp(raw_data_end_timestamp):
    if raw_data_end_timestamp == 0:
        return get_current_timestamp()
    else:
        return raw_data_end_timestamp


def create_raw_data_for_a_user(raw_data_configs, id):
    file_write_mode = "a"

    time_format = raw_data_configs["time_format"]
    raw_data_file_path = raw_data_configs["raw_data_file_path"]
    raw_data_start_timestamp = raw_data_configs["raw_data_generation_start_timestamp"]
    raw_data_end_timestamp = raw_data_configs["raw_data_generation_end_timestamp"]

    start = raw_data_configs["raw_data_consumption_range_start"]
    end = raw_data_configs["raw_data_consumption_range_end"]

    raw_data_end_timestamp = get_raw_data_end_timestamp(raw_data_end_timestamp)

    raw_data_granularity = raw_data_configs["raw_data_granularity_in_secs"]
    variable_fields_with_static_key = raw_data_configs["variable_fields_with_static_key"]
    dummy_raw_data_record = raw_data_configs["dummy_raw_data_record"]

    raw_data_records_for_a_user = []
    user_raw_data_consumption_map = []

    raw_data_record = populate_variable_fields_with_static_key(dummy_raw_data_record, variable_fields_with_static_key,
                                                               id)
    epoch_timestamp = raw_data_start_timestamp
    while epoch_timestamp <= raw_data_end_timestamp:
        consumption = get_random_usage_data(start, end)

        user_raw_data_consumption_map.append({
            str(epoch_timestamp): consumption
        })

        date_time = get_required_date_time_from_epoch(epoch_timestamp, time_format)

        single_raw_data_record_for_a_time = populate_consumption_and_date_time_into_raw_data_record(raw_data_record,
                                                                                                    consumption,
                                                                                                    date_time)
        raw_data_records_for_a_user.append(single_raw_data_record_for_a_time)
        epoch_timestamp = epoch_timestamp + raw_data_granularity

    write_list_into_file(raw_data_records_for_a_user, raw_data_file_path, file_write_mode)

    return user_raw_data_consumption_map


def create_billing_data_for_a_user(billing_data_configs, user_raw_data_consumption_map, billing_cycle_list, rate, id):
    file_write_mode = "a"

    billing_data_file_path = billing_data_configs["billing_data_file_path"]
    dummy_billing_data_record = billing_data_configs["dummy_billing_data_record"]
    variable_fields_with_static_key = billing_data_configs["variable_fields_with_static_key"]
    is_billing_end_date_inclusive = billing_data_configs["is_billing_end_date_inclusive"]

    user_billing_data_record = []

    agg_mode = "BC"
    aggregated_raw_data_per_bc = aggregate_raw_data(user_raw_data_consumption_map, agg_mode, billing_cycle_list,
                                                    is_billing_end_date_inclusive)

    billing_data_record = populate_variable_fields_with_static_key(dummy_billing_data_record,
                                                                   variable_fields_with_static_key, id)

    for data in aggregated_raw_data_per_bc:
        bc_start = data["bc_start"]
        bc_end = data["bc_end"]

        bc_duration = get_bc_duration(bc_start, bc_end)

        consumption = data["consumption"]

        cost = get_cost(consumption, rate)

        single_billing_data_record = populate_billing_data_cost_consumption_values(billing_data_record, cost,
                                                                                   consumption, bc_start, bc_end,
                                                                                   bc_duration)

        user_billing_data_record.append(single_billing_data_record)

    write_list_into_file(user_billing_data_record, billing_data_file_path, file_write_mode)


def get_bc_duration(bc_start, bc_end):
    bc_duration = str((datetime.strptime(bc_end, "%Y-%m-%d") - datetime.strptime(bc_start, "%Y-%m-%d")).days)
    return bc_duration


def get_cost(consumption, rate):
    cost = (consumption / rate).__round__(2)
    return cost


def get_configs_from_config_file(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    return data


def write_data_into_file(file_path, data, mode):
    with open(file_path, mode) as file:
        file.write(data)
    file.close()


def read_data_from_file():
    pass


def analyze_raw_data():
    pass


def analyze_billing_data():
    pass


def get_current_timestamp():
    current_epoch_timestamp = int(time.time())
    return current_epoch_timestamp


def get_epoch_from_date(date, date_format):
    epoch = int(datetime.strptime(date, date_format).timestamp())
    return epoch


def populate_variable_fields_with_static_key(record, variable_fields_with_static_key, id):
    for variable_column_field in variable_fields_with_static_key:
        value = variable_fields_with_static_key[variable_column_field]
        if id != -1:
            value = value + "_" + str(id)
        record = record.replace('{' + variable_column_field + '}', value)

    return record


def populate_consumption_and_date_time_into_raw_data_record(record, consumption, date_time):
    record = record.replace('{' + "consumption" + '}', str(consumption))
    record = record.replace('{' + "date_time" + '}', str(date_time))
    return record


def populate_billing_data_cost_consumption_values(record, cost, consumption, bc_start, bc_end, bc_duration):
    record = record.replace('{' + "consumption" + '}', str(consumption))
    record = record.replace('{' + "cost" + '}', str(cost))
    record = record.replace('{' + "bc_start" + '}', bc_start)
    record = record.replace('{' + "bc_end" + '}', bc_end)
    record = record.replace('{' + "bc_duration" + '}', bc_duration)
    return record


def get_required_date_time_from_epoch(epoch, time_format):
    date_time = datetime.fromtimestamp(epoch).strftime(time_format)
    return date_time


def get_random_usage_data(start, end):
    usage = random.uniform(start, end).__round__(2)
    return usage


def write_list_into_file(list_data, file_path, mode):
    data = ""
    for values in list_data:
        data = data + values + "\n"

    write_data_into_file(file_path, data, mode)


def aggregate_raw_data(user_raw_data_consumption_map, agg_mode, billing_cycle_list, is_billing_end_date_inclusive):
    aggregated_data = []

    if agg_mode == "DAY":
        aggregated_data = aggregate_raw_data_on_day(user_raw_data_consumption_map)
    elif agg_mode == "MONTH":
        aggregated_data = aggregate_raw_data_on_month(user_raw_data_consumption_map)
    elif agg_mode == "BC":
        if len(billing_cycle_list) > 0:
            aggregated_data = aggregate_raw_data_on_bc(user_raw_data_consumption_map, billing_cycle_list,
                                                       is_billing_end_date_inclusive)

    return aggregated_data


def aggregate_raw_data_on_day(user_raw_data_consumption_map):
    pass


def aggregate_raw_data_on_month(user_raw_data_consumption_map):
    pass


def aggregate_raw_data_on_bc(user_raw_data_consumption_map, billing_cycle_list, is_billing_end_date_inclusive):
    aggregated_data = []
    for billing_cycle in billing_cycle_list:

        bc_date_format = '%Y-%m-%d'
        bc_start_date = billing_cycle["start"]
        bc_end_date = billing_cycle["end"]

        bc_start_timestamp = get_epoch_from_date(bc_start_date, bc_date_format)
        bc_end_timestamp = get_epoch_from_date(bc_end_date, bc_date_format)

        if not is_billing_end_date_inclusive:
            bc_end_timestamp = bc_end_timestamp - 86400

        consumption_for_this_bc = extract_consumption_data_in_window(user_raw_data_consumption_map, bc_start_timestamp,
                                                                     bc_end_timestamp)

        aggregated_data.append({
            "bc_start": bc_start_date,
            "bc_end": bc_end_date,
            "consumption": consumption_for_this_bc
        })

    return aggregated_data


def extract_consumption_data_in_window(consumption_data, start, end):
    current_window_consumption = 0
    for data in consumption_data:
        timestamp = list(data.keys())[0]
        consumption_timestamp = int(timestamp)
        if consumption_timestamp >= start and consumption_timestamp <= end:
            consumption = data[timestamp]
            current_window_consumption = current_window_consumption + consumption

    return current_window_consumption.__round__(2)


def get_absolute_file_path_from_relative_path(relative_path):
    absolute_path = os.path.abspath(relative_path)
    return absolute_path


def create_plots():
    pass


def getBillingCycles(bc_config_value, user_inputs, bc_range_start, bc_range_end):
    billing_cycle_list = []
    bc_code = bc_config_value["bc_code"]
    if bc_code !=-1:
        billing_cycle_list = get_bc_schedules_from_api(user_inputs, bc_code, bc_range_start, bc_range_end)
    else:
        billing_cycle_list = configs["bc_schedule"]["billing_cycles"]

    return billing_cycle_list


def get_bc_schedules_from_api(user_inputs, bc_code, bc_range_start, bc_range_end):
    parameters = {}
    pilot_id = user_inputs["pilot_id"]
    data_server_url = user_inputs["data_server_url"]
    parameters["access_token"] = user_inputs["access_token"]

    bc_schedule_api = "/2.1/utilityBillingCycles/utility/" + str(pilot_id) + "/identifier/" + str(bc_code)

    url = data_server_url + bc_schedule_api
    api_response = getApiCall(url, parameters)

    schedules_data = api_response["payload"]
    schedules_in_date_format = []

    for schedule in schedules_data:
        start_epoch = schedule["validFrom"]
        end_epoch = schedule["validTo"]
        keep_this_bc = is_bc_in_start_end_range(bc_range_start, bc_range_end, start_epoch, end_epoch)
        if keep_this_bc == True:
            schedules_in_date_format.append({"start": get_date_time_from_epoch_timestamp(start_epoch, "%Y-%m-%d"),
                                             "end": get_date_time_from_epoch_timestamp(end_epoch, "%Y-%m-%d")})

    return schedules_in_date_format


def get_date_time_from_epoch_timestamp(epoch_timestamp, date_format):
    # Convert the epoch timestamp to a datetime object
    dt_object = datetime.fromtimestamp(epoch_timestamp)
    # Format the datetime object as "yyyy-mm-dd"
    formatted_date = dt_object.strftime(date_format)
    return formatted_date


def is_bc_in_start_end_range(bc_range_start, bc_range_end, bc_start, bc_end):
    if bc_range_start>=bc_start and  bc_range_start<=bc_end:
        return True
    elif bc_range_start<bc_start and  bc_range_end>=bc_end:
        return True
    elif bc_range_end>=bc_start and  bc_range_end<bc_end:
        return True

    return False


def getApiCall(url, params):
    try:
        response = requests.get(url=url, params=params)
        if response.status_code == 200:
            response_json = response.json()
    except Exception as e:
        print("exception occured while fetching bc schedule data from ", url, "\n", e)
    return response_json


if __name__ == '__main__':
    print("hello to user data creation program")
    config_file_path = get_absolute_file_path_from_relative_path("config.json")
    configs = get_configs_from_config_file(config_file_path)

    create_users = configs["user_inputs"]["create_user_enrollment"]
    create_meters = configs["user_inputs"]["create_user_enrollment"]
    create_raw_data = configs["user_inputs"]["create_user_enrollment"]
    create_billing_data = configs["user_inputs"]["create_user_enrollment"]

    if create_users:
        print("creating user enrollment records")
        user_configs = configs["user_enrollment"]
        create_user_enrollment_record(user_configs)
        print("created user enrollment records")

    if create_meters:
        print("creating meter enrollment records")
        meter_configs = configs["meter_enrollment"]
        meters_to_be_created = user_configs["users_to_be_created"]
        create_meter_enrollment_record(meter_configs, meters_to_be_created, user_configs["user_id_start"])
        print("created meter enrollment records")

    create_raw_and_billing_for_all_users = ""
    only_update_raw_data = ""
    update_raw_and_billing_data = ""

    user_id_start = user_configs["user_id_start"]
    raw_data_configs = configs["raw_data"]
    billing_cycle_list = getBillingCycles(configs["bc_schedule"], configs["user_inputs"],
                                          raw_data_configs["raw_data_generation_start_timestamp"],
                                          get_raw_data_end_timestamp(
                                              raw_data_configs["raw_data_generation_end_timestamp"]))

    if create_raw_data and create_billing_data:
        print("creating raw data files along with billing data files...")


        unique_users_count = configs["user_enrollment"]["users_to_be_created"]

        for id in range(user_id_start, user_id_start + unique_users_count):
            print("creating raw data files...")
            user_raw_data_consumption_map = create_raw_data_for_a_user(raw_data_configs, id)

            print("creating billing data files...")
            billing_data_configs = configs["billing_data"]

            rate = configs["user_inputs"]["default_rate"]
            create_billing_data_for_a_user(billing_data_configs, user_raw_data_consumption_map, billing_cycle_list,
                                           rate,
                                           id)

    elif create_raw_data:
        print("creating raw data files...")
        create_raw_data_for_a_user(raw_data_configs, user_id_start)
