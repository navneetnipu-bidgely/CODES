#!/bin/python3
# please get these packages installed before executing this program.

# packages required to handle json data structure or put api responses into json
import json

# packages required to handle mathematical operations like min,ceil or floor functions
import math

# packages required for executing multithreading
import threading

# packages required to handle api callings
import requests

# packages required to handle date,time,locale etc conversions or releted operations
import datetime
import pytz

# packages required to handle excel sheet read or write operations
from xlwt import Workbook

# packages required to handle operations releted to stuff in local computer
import os

# packages required to handle logging operations like create log file, write in log file at different log level like info,debug,warning etc
import logging

# Below are the required user input variables

# Data server url for pseg (prod-na)
DATA_SERVER_URL = "https://naapi.bidgely.com"

# Access token for authentication of APIs
ACCESS_TOKEN = "40619138-b78f-4851-98ca-588b61fd3bcf"

# Putting payload parameters required for API call
# can be edited if needed to add any other api parameters
PARAMS = {"access_token": ACCESS_TOKEN}

# limiting number of threads to restrict any cpu overloading
NO_OF_THREADS_TO_BE_MADE = 10

# chunk size that will be used to run all threads (NO_OF_THREADS_TO_BE_MADE) on particular chunk of users
TOU_CHUNK_SIZE = 2
NON_TOU_CHUNK_SIZE = 2

# time zone of pilot
TIMEZONE = "America/New_York"

# time zone conversion (not user input)
NY_TZ = pytz.timezone('America/New_York')

# mode of data to be fetched (can be day,month year etc.)
MODE = "month"

# home id of the user (generally 1)
HID = 1

# t0:start time of data to be fetched from (default is 0)
DEFAULT_T0 = 0

# t1:end time of data to be fetched (default is current timestamp)
DEFAULT_T1 = 1676291576

# locale of the pilot (depends upon pilot)
LOCALE = "en_US"

# appliance ID's list
APPLIANCE_ID_LIST = [18, 4]

# survey question list
SURVEY_QUESTION_LIST = ["Q1", "Q6"]

# measurementType
MEASUREMENT_TYPE = "ELECTRIC"

# tou file path
TOU_FILE_PATH = "/Users/navneetnipu/Desktop/TOU_UUID.txt"

# nontou file path
NONTOU_FILE_PATH = "/Users/navneetnipu/Desktop/NONTOU_UUID.txt"

# appliance name mapping
APPLIANCE_NAME_MAPPING = {18: "EV", 4: "Heating"}

# rate plan to category mapping to find out user belongs to which category based on ratePlanId
RATE_PLAN_TO_CATEGORY_MAPPING = {190: "tou", 191: "tou", 192: "tou", 193: "tou", 180: "tier", 580: "tier"}

# rate plan mapping
RATE_PLAN_MAPPING = {1: 180, 10: 580, 37: 190, 41: 191, 42: 192, 34: 193}

# cTypes programId
TIER_PROGRAM_ID = "0fa90f13-2ec8-4768-b1b1-a764d57955c9"
TOU_PROGRAM_ID = "63302766-1cc4-43dd-9bd9-70ed72b2ddf5"
# rate category to proramID mapping(for internal use)
FIND_PROGRAM_ID_FROM_RATE_CATEGORY = {"tou": TOU_PROGRAM_ID, "tier": TIER_PROGRAM_ID}

# last 2 completed calander months start and end timestamps (december 2022 and january 2023)
LAST_COMPLETED_CALENDER_START_TIMESTAMP = 1669870800
LAST_COMPLETED_CALENDER_END_TIMESTAMP = 1672545200
CURRENT_COMPLETED_CALENDER_START_TIMESTAMP = 1672549200
CURRENT_COMPLETED_CALENDER_END_TIMESTAMP = 1675227500

# initializing CURRENT_COMPLETED_MONTH and lastCompletedMonth variables that will hold cycle data at user level
# They will be used for timestamps when data in JSON_REPORT are changed to MMDDYYYY
CURRENT_COMPLETED_MONTH = {}
LAST_COMPLETED_MONTH = {}

# get the current date and time
current_datetime = datetime.datetime.now()

# format the current date and time as a string
formatted_datetime = current_datetime.strftime("%d%m%Y%H%M%S")
# file path for logger

# create a log file
with open("/Users/navneetnipu/Desktop/psegReportLogFile" + formatted_datetime + ".log", 'w') as file:
    pass

LOG_FILE_PATH = "/Users/navneetnipu/Desktop/psegReportLogFile" + formatted_datetime + ".log"

# Configure the logging module
# change the level config for different log level like log,debug,warning etc.
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO)

# list of apis to be used in below code
# {{url}}/v2.0/users/{{uuid}}/
# {{url}}/billingdata/users/{{uuid}}/homes/{{hid}}/billingcycles?t0={{t0}}&t1={{t1}}
# {{url}}/billingdata/users/{{uuid}}/homes/{{hid}}/utilitydata?t0={{t0}}&t1={{t1}}
# {{url}}/streams/users/{{uuid}}/homes/{{hid}}/tbappdata/monthly.json?t0={{t0}}&t1={{t1}}
# {{url}}/v2.0/users/{{uuid}}/homes/1/survey?locale=en_US
# {{url}}/billingdata/users/{{uuid}}/homes/1/aggregatedCost/18/tou?planNumber=1&t0=1662004800&t1=1664596500&mode=month&tz=America/New_York&access_token={{accessToken}}


USER_DETAILS_API = DATA_SERVER_URL + "/v2.0/users/{uuid}/"
BILLING_DATA_API = DATA_SERVER_URL + "/billingdata/users/{uuid}/homes/" + str(
    HID) + "/utilitydata?t0={t0}&t1={t1}" + "&measurementType=" + MEASUREMENT_TYPE
DISAGG_DATA_API = DATA_SERVER_URL + "/streams/users/{uuid}/homes/" + str(
    HID) + "/tbappdata/monthly.json?t0={t0}&t1={t1}"
SURVEY_API = DATA_SERVER_URL + "/v2.0/users/{uuid}/homes/" + str(HID) + "/survey?locale=" + LOCALE
AGGREGATED_COST_API = DATA_SERVER_URL + "/billingdata/users/{uuid}/homes/" + str(
    HID) + "/aggregatedCost/{appId}/{cType}?planNumber={planNumber}&t0={t0}&t1={t1}" + "&mode={mode}" + "&tz=" + TIMEZONE

# uuid report (OUTPUT) data stored in json format that will be later on exported to excel sheet
'''
    # JSON_REPORT datastructure
    JSON_REPORT={
    uuid1:{
        "RatePlanID":value,
        "PlanNumber":value,
        "RatePlanSchedule":value,
        "LastMonth":value,
        "CurrentMonth":value,
        "EVDetectedInItemizationLastMonth":value,
        "EVDetectedInItemizationCurrentMonth":value,
        "HeatingDetectedInItemizationLastMonth":value,
        "HeatingDetectedInItemizationCurrentMonth":value,
        "EVansweredYESInSurvey":value,
        "HeatingAnsweredYESInSurvey":value,
        "TotalAggregatedEVConsumptionInCurrentCalendarMonth":value,
        "TotalAggregatedEVCostInCurrentCalendarMonth":value,
        "TotalAggregatedEVConsumptionInLastCalendarMonth":value,
        "TotalAggregatedEVCostInLastCalendarMonth":value
        },
    uuid2{...},
    ...}

'''

# initializing output variable globally with empty json
JSON_REPORT = {}

# Excel sheet header list
SHEET_HEADER_DATA = ["UUID", "RatePlanID", "PlanNumber", "RatePlanSchedule", "LastMonth", "CurrentMonth",
                     "EVDetectedInItemizationLastMonth", "EVDetectedInItemizationCurrentMonth",
                     "HeatingDetectedInItemizationLastMonth", "HeatingDetectedInItemizationCurrentMonth",
                     "EVansweredYESInSurvey", "HeatingAnsweredYESInSurvey",
                     "TotalAggregatedEVConsumptionInCurrentCalendarMonth",
                     "TotalAggregatedEVCostInCurrentCalendarMonth", "TotalAggregatedEVConsumptionInLastCalendarMonth",
                     "TotalAggregatedEVCostInLastCalendarMonth"]

'''
    below are the functions to get required user data to be populated in excel sheet later on.
    USER_API_DATA (MULTITHREADED) => JSON_DATA => EXCEL SHEET
'''

TOU_UUID = []
NON_TOU_UUID = []


# function to get list of uuids to perform api calling and store it in TOU_UUID and NON_TOU_UUID variable in list format
def get_uuid_list_from_file(file_path):
    # read from tou txt file for uuid list
    try:

        with open(file_path, "r") as openfile:
            user_list = openfile.read().splitlines()

        return user_list

    except Exception as e:
        print("exception occured while getting uuid list from file ", file_path)
        print(e)


'''
    rate_info structure.
    rate_info={ uuid:{RatePlanID:value,PlanNumber:value,RatePlanSchedule:{oldInfo:{oldStartTime:value,oldEndTime:value,oldPlanNumber:value},newInfo:{newStartTime:value,newEndTime:value,NewPlanNumber:value}}}}
'''


# function to get rates releted information for a user using api:{{url}}/v2.0/users/{{uuid}}/ and store it in rate_info variable in json format.
def get_uuid_rate_info(uuid):
    # initializing some data structures to empty json by default
    JSON_REPORT[uuid] = {}
    rate_plan_schedule = {}
    rate = {}

    # getting user details api response using USER_DETAILS_API in json format and extracting required json part from it
    api_data = api_call(api=USER_DETAILS_API.format(uuid=uuid), method='GET', params=PARAMS, data="")["payload"][
        "homeAccounts"]

    # storing rate and ratesSchedule data separatly from api json data

    if "rate" in api_data and api_data["rate"] != None:
        rate = api_data["rate"]

        # populating rate specific data into JSON_REPORT[uuid]
        JSON_REPORT[uuid]["RatePlanID"] = rate["ratePlanId"]
        JSON_REPORT[uuid]["PlanNumber"] = rate["planNumber"]

    if api_data["ratesSchedule"] != None:
        ratesSchedule = json.loads(api_data["ratesSchedule"])

        # calculating ratesSchedule list length so as to get last and second last occurence of the list for new and old rate information
        rates_schedule_length = len(ratesSchedule)

        # new rate information is the last json occurence of ratesSchedule list
        new_rate_info = ratesSchedule[rates_schedule_length - 1]
        rate_plan_schedule["newInfo"] = {
            "newStartTime": NY_TZ.localize(datetime.datetime.fromtimestamp(new_rate_info["startTime"])).strftime(
                '%d/%m/%Y'),
            "newEndTime": NY_TZ.localize(datetime.datetime.fromtimestamp(new_rate_info["endTime"])).strftime(
                '%d/%m/%Y'), "newPlanNumber": new_rate_info["metaData"]["planNumber"]}

        # old rate information is the second last json occurence of ratesSchedule list if contains more than 2 occurences otherwise old rate information will be same as new rate information
        if rates_schedule_length >= 2:
            old_rate_info = ratesSchedule[rates_schedule_length - 2]
            rate_plan_schedule["oldInfo"] = {
                "oldStartTime": NY_TZ.localize(datetime.datetime.fromtimestamp(old_rate_info["startTime"])).strftime(
                    '%d/%m/%Y'),
                "oldEndTime": NY_TZ.localize(datetime.datetime.fromtimestamp(old_rate_info["endTime"])).strftime(
                    '%d/%m/%Y'), "oldPlanNumber": old_rate_info["metaData"]["planNumber"]}

    # populating user specific rateSchedule data into global variable JSON_REPORT that will contain rate data for all listed users
    JSON_REPORT[uuid]["RatePlanSchedule"] = rate_plan_schedule


# function to get start and end timestamp for last 2 completed cycles and convert thetiestamp to DDMMYYYY format but keep the original timestamps for further use
def get_completed_billing_cycles(uuid, no_of_last_completed_cycles):
    # by default making the values empty json
    JSON_REPORT[uuid]["CurrentMonth"] = {}
    JSON_REPORT[uuid]["LastMonth"] = {}

    api_data_json = api_call(api=BILLING_DATA_API.format(uuid=uuid, t0=DEFAULT_T0, t1=DEFAULT_T1), method='GET',
                             params=PARAMS, data="")

    # after getting the api data, we need to sort the json data as per key in descending order and
    # iterate over the data to find last two completed cycles (bidgelyGeneratedInvoice=false/true doesnt matter)

    billingStartTimestamps_list = list(api_data_json.keys())
    # sorting the start timestamps in decending order
    billingStartTimestamps_list.sort(reverse=True)

    # for storing last completed cycles information,initializing last_completed_cycles_info
    # last_completed_cycles_info data structure : last_completed_cycles_info={1:{billingStartTs:value,billingEndTs:value},2:{billingStartTs:value,billingEndTs:value},..}
    last_completed_cycles_info = {}

    # variable to take a count of completed cycles stored in last_completed_cycles_info which should not exceed no_of_last_completed_cycles
    completed_cycle_index = 1
    for startTimestamp in billingStartTimestamps_list:
        last_completed_cycles_info[completed_cycle_index] = {
            "billingStartTs": api_data_json[startTimestamp]["billingStartTs"],
            "billingEndTs": api_data_json[startTimestamp]["billingEndTs"]}
        if completed_cycle_index < no_of_last_completed_cycles:
            completed_cycle_index += 1
        else:
            break

    if 1 in last_completed_cycles_info:
        # populating current_completed_cycles_info in global variables
        CURRENT_COMPLETED_MONTH[uuid] = {"billingStartTs": last_completed_cycles_info[1]["billingStartTs"],
                                         "billingEndTs": last_completed_cycles_info[1]["billingEndTs"]}

        # adding the current_completed_cycles_info data to JSON_REPORT
        JSON_REPORT[uuid]["CurrentMonth"] = {"billingStartTs": NY_TZ.localize(
            datetime.datetime.fromtimestamp(CURRENT_COMPLETED_MONTH[uuid]["billingStartTs"])).strftime('%m%d%Y'),
                                             "billingEndTs": NY_TZ.localize(datetime.datetime.fromtimestamp(
                                                 CURRENT_COMPLETED_MONTH[uuid]["billingEndTs"])).strftime('%m%d%Y')}

    if 2 in last_completed_cycles_info:
        # populating last_completed_cycles_info in global variables
        LAST_COMPLETED_MONTH[uuid] = {"billingStartTs": last_completed_cycles_info[2]["billingStartTs"],
                                      "billingEndTs": last_completed_cycles_info[2]["billingEndTs"]}

        # adding the last_completed_cycles_info data to JSON_REPORT
        JSON_REPORT[uuid]["LastMonth"] = {"billingStartTs": NY_TZ.localize(
            datetime.datetime.fromtimestamp(LAST_COMPLETED_MONTH[uuid]["billingStartTs"])).strftime('%m%d%Y'),
                                          "billingEndTs": NY_TZ.localize(datetime.datetime.fromtimestamp(
                                              LAST_COMPLETED_MONTH[uuid]["billingEndTs"])).strftime('%m%d%Y')}


# function to get aggregatedCost and consumption information for particular app id (for now EV, appId=18)
def get_billing_data_info(uuid, PlanNumber):
    # initializing TotalAggregatedEVConsumptionInCurrentCalendarMonth,TotalAggregatedEVCostInCurrentCalendarMonth,TotalAggregatedEVConsumptionInLastCalendarMonth,TotalAggregatedEVCostInLastCalendarMonth to null values

    JSON_REPORT[uuid]["TotalAggregatedEVConsumptionInCurrentCalendarMonth"] = ""
    JSON_REPORT[uuid]["TotalAggregatedEVCostInCurrentCalendarMonth"] = ""
    JSON_REPORT[uuid]["TotalAggregatedEVConsumptionInLastCalendarMonth"] = ""
    JSON_REPORT[uuid]["TotalAggregatedEVCostInLastCalendarMonth"] = ""

    '''
        # check if user has trasitioned rates or not
        # if transitioned, whether it is from same type(tier rate1=>tier rate2 like that) or cross type(tier=>tou or tou=>tier)
        # if user is transitioned rates then call api with mode=day and t0 and t1 should be previous and current rate slab timestamps
        # take the aggregated cost and consumption from respective api 
        ## for pseg for now, if rateSchedule is null we cant find rate transitioned user
    '''

    # initializing the cost variables to 0
    current_month_billing_cost = 0
    last_month_billing_cost = 0

    # initializing the consumption variables to 0
    current_month_aggregated_consumption = 0
    last_month_aggregated_consumption = 0

    if JSON_REPORT[uuid]["RatePlanSchedule"] == {} or len(JSON_REPORT[uuid]["RatePlanSchedule"]) == 1:
        '''
            # no need to find rate transitions data
            # first find the rate category of user through ratePlanId and RATE_TO_CATEGORY_MAPPING
            # Then call the respective aggregated Cost and consumption APIs
            # Then add the total consumptions for all timestamps to find the aggregated consumtion
            # same for cost to find the aggregated cost
        '''

        rate_category = RATE_PLAN_TO_CATEGORY_MAPPING[int(JSON_REPORT[uuid]["RatePlanID"])]
        PlanNumber = JSON_REPORT[uuid]["PlanNumber"]

        # for current completed month

        # adding program_id to api parameter locally
        params = PARAMS
        params["programId"] = FIND_PROGRAM_ID_FROM_RATE_CATEGORY[rate_category]

        # finding aggreagted cost

        api_data_billingCost_CurrentMonth_json = api_call(
            api=AGGREGATED_COST_API.format(uuid=uuid, appId=APPLIANCE_ID_LIST[0], cType="billing_cost",
                                           planNumber=PlanNumber, t0=CURRENT_COMPLETED_CALENDER_START_TIMESTAMP,
                                           t1=CURRENT_COMPLETED_CALENDER_END_TIMESTAMP, mode="month"), method='GET',
            params=params, data="")

        # calculating aggregated billing cost for current month
        for timestamp in api_data_billingCost_CurrentMonth_json:
            current_month_billing_cost += api_data_billingCost_CurrentMonth_json[timestamp]["cost"]

        # finding aggregated consumption

        api_data_tou_consumption_currentMonth_json = api_call(
            api=AGGREGATED_COST_API.format(uuid=uuid, appId=APPLIANCE_ID_LIST[0], cType=rate_category,
                                           planNumber=PlanNumber, t0=CURRENT_COMPLETED_CALENDER_START_TIMESTAMP,
                                           t1=CURRENT_COMPLETED_CALENDER_END_TIMESTAMP, mode="month"), method='GET',
            params=params, data="")

        # calculating aggregated consumption for current month
        for timestamp in api_data_tou_consumption_currentMonth_json:
            data = api_data_tou_consumption_currentMonth_json[timestamp][rate_category + "AggData"][
                rate_category + "RrcMap"]
            for category in data:
                current_month_aggregated_consumption += data[category]["tierCons"]

        # for last completed month

        # finding aggregated cost

        api_data_billingCost_LastMonth_json = api_call(
            api=AGGREGATED_COST_API.format(uuid=uuid, appId=APPLIANCE_ID_LIST[0], cType="billing_cost",
                                           planNumber=PlanNumber, t0=LAST_COMPLETED_CALENDER_START_TIMESTAMP,
                                           t1=LAST_COMPLETED_CALENDER_END_TIMESTAMP, mode="month"), method='GET',
            params=params, data="")

        # calculating aggregated billing cost for last month
        for timestamp in api_data_billingCost_LastMonth_json:
            last_month_billing_cost += api_data_billingCost_LastMonth_json[timestamp]["cost"]

        # finding aggreagted consumtion

        api_data_tou_consumption_LastMonth_json = api_call(
            api=AGGREGATED_COST_API.format(uuid=uuid, appId=APPLIANCE_ID_LIST[0], cType=rate_category,
                                           planNumber=PlanNumber, t0=LAST_COMPLETED_CALENDER_START_TIMESTAMP,
                                           t1=LAST_COMPLETED_CALENDER_END_TIMESTAMP, mode="month"), method='GET',
            params=params, data="")

        # calculating aggregated consumption for last month
        for timestamp in api_data_tou_consumption_LastMonth_json:
            data = api_data_tou_consumption_LastMonth_json[timestamp][rate_category + "AggData"][
                rate_category + "RrcMap"]
            for category in data:
                last_month_aggregated_consumption += data[category]["tierCons"]



    elif JSON_REPORT[uuid]["RatePlanSchedule"] != {} or len(JSON_REPORT[uuid]["RatePlanSchedule"]) > 1:
        '''
            # in this case we need to find rate_effective_timestamp
            # rate_effective_timestamp=start_timestamp of last occurence of rateSchedule json data in user details api.
            # find in which calender month rate_effective_timestamp falls (either current or last)
            # find the particular t0 and t1 slabs
            # then fetch the api data using proper parameters
        '''

        params = PARAMS

        # getting user details api response using USER_DETAILS_API in json format and extracting required rateSchedule json part from it
        api_data = api_call(api=USER_DETAILS_API.format(uuid=uuid), method='GET', params=PARAMS, data="")["payload"][
            "homeAccounts"]
        rates_schedule = json.loads(api_data["ratesSchedule"])

        # finding the required data from rates_schedule to call the billing api

        # finding old rates data
        rates_schedule_len = len(rates_schedule)
        old_rate_plan_number = int(rates_schedule[rates_schedule_len - 2]["metaData"]["planNumber"])
        old_rate_category = RATE_PLAN_TO_CATEGORY_MAPPING[RATE_PLAN_MAPPING[old_rate_plan_number]]

        # finding new rates data
        new_rate_plan_number = int(rates_schedule[rates_schedule_len - 1]["metaData"]["planNumber"])
        new_rate_category = RATE_PLAN_TO_CATEGORY_MAPPING[RATE_PLAN_MAPPING[new_rate_plan_number]]
        rate_effective_timestamp = rates_schedule[rates_schedule_len - 1]["endTime"]

        # finding the rate time slab from rate_effective_timestamp
        start_end_timestamp_slab = get_start_end_timeslab_for_rate_transition(rate_effective_timestamp)

        # calculate the aggregated consumption and cost for different time slabs and different rate category

        # calculating aggregated cost and consumption for current completed month time slabs

        # current_month_billing_cost
        # current_month_aggregated_consumption
        for time_slab in start_end_timestamp_slab["current_month"]:

            params = PARAMS

            if time_slab["new_rate_plan_applied"] == True:

                # adding program_id to api parameter locally using rate_category
                params["programId"] = FIND_PROGRAM_ID_FROM_RATE_CATEGORY[new_rate_category]

                # finding aggregated cost
                api_data_billingCost_CurrentMonth_json = api_call(
                    api=AGGREGATED_COST_API.format(uuid=uuid, appId=APPLIANCE_ID_LIST[0], cType="billing_cost",
                                                   planNumber=new_rate_plan_number, t0=time_slab["start"],
                                                   t1=time_slab["end"], mode=time_slab["mode"]), method='GET',
                    params=params, data="")

                # calculating aggregated billing cost for current month
                for timestamp in api_data_billingCost_CurrentMonth_json:
                    current_month_billing_cost += api_data_billingCost_CurrentMonth_json[timestamp]["cost"]

                # finding aggregated consumption
                api_data_tou_consumption_currentMonth_json = api_call(
                    api=AGGREGATED_COST_API.format(uuid=uuid, appId=APPLIANCE_ID_LIST[0], cType=new_rate_category,
                                                   planNumber=new_rate_plan_number, t0=time_slab["start"],
                                                   t1=time_slab["end"], mode=time_slab["mode"]), method='GET',
                    params=params, data="")

                for timestamp in api_data_tou_consumption_currentMonth_json:
                    data = api_data_tou_consumption_currentMonth_json[timestamp][new_rate_category + "AggData"][
                        new_rate_category + "RrcMap"]
                    for category in data:
                        current_month_aggregated_consumption += data[category]["tierCons"]

            else:
                # adding program_id to api parameter locally using rate_category
                params["programId"] = FIND_PROGRAM_ID_FROM_RATE_CATEGORY[old_rate_category]

                # finding aggregated cost
                api_data_billingCost_CurrentMonth_json = api_call(
                    api=AGGREGATED_COST_API.format(uuid=uuid, appId=APPLIANCE_ID_LIST[0], cType="billing_cost",
                                                   planNumber=old_rate_category, t0=time_slab["start"],
                                                   t1=time_slab["end"], mode=time_slab["mode"]), method='GET',
                    params=params, data="")

                # calculating aggregated billing cost for current month
                for timestamp in api_data_billingCost_CurrentMonth_json:
                    current_month_billing_cost += api_data_billingCost_CurrentMonth_json[timestamp]["cost"]

                # finding aggregated consumption
                api_data_tou_consumption_currentMonth_json = api_call(
                    api=AGGREGATED_COST_API.format(uuid=uuid, appId=APPLIANCE_ID_LIST[0], cType=old_rate_category,
                                                   planNumber=old_rate_plan_number, t0=time_slab["start"],
                                                   t1=time_slab["end"], mode=time_slab["mode"]), method='GET',
                    params=params, data="")

                # calculating aggregated consumption for last completed month
                for timestamp in api_data_tou_consumption_currentMonth_json:
                    data = api_data_tou_consumption_currentMonth_json[timestamp][old_rate_category + "AggData"][
                        old_rate_category + "RrcMap"]
                    for category in data:
                        current_month_aggregated_consumption += data[category]["tierCons"]

        # calculating aggregated cost and consumption for last completed month time slabs

        # last_month_billing_cost
        # last_month_aggregated_consumption
        for time_slab in start_end_timestamp_slab["last_month"]:

            params = PARAMS

            if time_slab["new_rate_plan_applied"] == True:
                # adding program_id to api parameter locally using rate_category
                params["programId"] = FIND_PROGRAM_ID_FROM_RATE_CATEGORY[new_rate_category]

                # finding aggregated cost

                api_data_billingCost_LastMonth_json = api_call(
                    api=AGGREGATED_COST_API.format(uuid=uuid, appId=APPLIANCE_ID_LIST[0], cType="billing_cost",
                                                   planNumber=new_rate_plan_number, t0=time_slab["start"],
                                                   t1=time_slab["end"], mode=time_slab["mode"]), method='GET',
                    params=params, data="")

                # calculating aggregated billing cost for last month
                for timestamp in api_data_billingCost_LastMonth_json:
                    last_month_billing_cost += api_data_billingCost_LastMonth_json[timestamp]["cost"]

                # finding aggregated consumption
                api_data_tou_consumption_lastMonth_json = api_call(
                    api=AGGREGATED_COST_API.format(uuid=uuid, appId=APPLIANCE_ID_LIST[0], cType=new_rate_category,
                                                   planNumber=new_rate_plan_number, t0=time_slab["start"],
                                                   t1=time_slab["end"], mode=time_slab["mode"]), method='GET',
                    params=params, data="")

                # calculating aggregated consumption for last completed month
                for timestamp in api_data_tou_consumption_lastMonth_json:
                    data = api_data_tou_consumption_lastMonth_json[timestamp][new_rate_category + "AggData"][
                        new_rate_category + "RrcMap"]
                    for category in data:
                        last_month_aggregated_consumption += data[category]["tierCons"]

            else:
                # adding program_id to api parameter locally using rate_category
                params["programId"] = FIND_PROGRAM_ID_FROM_RATE_CATEGORY[old_rate_category]

                # finding aggregated cost

                api_data_billingCost_LastMonth_json = api_call(
                    api=AGGREGATED_COST_API.format(uuid=uuid, appId=APPLIANCE_ID_LIST[0], cType="billing_cost",
                                                   planNumber=old_rate_plan_number, t0=time_slab["start"],
                                                   t1=time_slab["end"], mode=time_slab["mode"]), method='GET',
                    params=params, data="")

                # calculating aggregated billing cost for last month
                for timestamp in api_data_billingCost_LastMonth_json:
                    last_month_billing_cost += api_data_billingCost_LastMonth_json[timestamp]["cost"]

                # finding aggregated cost
                api_data_tou_consumption_lastMonth_json = api_call(
                    api=AGGREGATED_COST_API.format(uuid=uuid, appId=APPLIANCE_ID_LIST[0], cType=old_rate_category,
                                                   planNumber=old_rate_plan_number, t0=time_slab["start"],
                                                   t1=time_slab["end"], mode=time_slab["mode"]), method='GET',
                    params=params, data="")

                # calculating aggregated consumption for last month
                for timestamp in api_data_tou_consumption_lastMonth_json:
                    data = api_data_tou_consumption_lastMonth_json[timestamp][old_rate_category + "AggData"][
                        old_rate_category + "RrcMap"]
                    for category in data:
                        last_month_aggregated_consumption += data[category]["tierCons"]

    # populating aggregated cost data to JSON_RESPORT for particular uuid

    if current_month_billing_cost != 0:
        JSON_REPORT[uuid]["TotalAggregatedEVCostInCurrentCalendarMonth"] = current_month_billing_cost
    else:
        JSON_REPORT[uuid]["TotalAggregatedEVCostInCurrentCalendarMonth"] = ""

    if last_month_billing_cost != 0:
        JSON_REPORT[uuid]["TotalAggregatedEVCostInLastCalendarMonth"] = last_month_billing_cost
    else:
        JSON_REPORT[uuid]["TotalAggregatedEVCostInLastCalendarMonth"] = ""

    # populating aggregated consumption data to JSON_RESPORT for particular uuid

    if current_month_aggregated_consumption != 0:
        JSON_REPORT[uuid]["TotalAggregatedEVConsumptionInCurrentCalendarMonth"] = current_month_aggregated_consumption
    else:
        JSON_REPORT[uuid]["TotalAggregatedEVConsumptionInCurrentCalendarMonth"] = ""

    if last_month_aggregated_consumption != 0:
        JSON_REPORT[uuid]["TotalAggregatedEVConsumptionInLastCalendarMonth"] = last_month_aggregated_consumption
    else:
        JSON_REPORT[uuid]["TotalAggregatedEVConsumptionInLastCalendarMonth"] = ""


# function to get the disagg data for different appliances
def get_disagg_data(uuid):
    # fetching each appliance data available in APPLIANCE_ID_LIST
    for appId in APPLIANCE_ID_LIST:
        # defining the t0 and t1 from last completed cycles data stored in JSON_REPORT for give uuid

        # current completed cycle
        current_completed_cycles_data = CURRENT_COMPLETED_MONTH[uuid]
        t0 = current_completed_cycles_data["billingStartTs"]
        t1 = current_completed_cycles_data["billingEndTs"]
        api_data_json = api_call(api=DISAGG_DATA_API.format(uuid=uuid, t0=t0, t1=t1), method='GET', params=PARAMS,
                                 data="")
        # by default if appId is not present in current month, it will store default value
        JSON_REPORT[uuid][APPLIANCE_NAME_MAPPING[appId] + "DetectedInItemizationCurrentMonth"] = "appId " + str(
            appId) + " not present in Itemization"
        for disagg_data in api_data_json:
            if disagg_data["appId"] == appId:
                JSON_REPORT[uuid][APPLIANCE_NAME_MAPPING[appId] + "DetectedInItemizationCurrentMonth"] = {
                    "appId": appId, "value": disagg_data["value"]}

        # last completed cycle
        last_completed_cycles_data = LAST_COMPLETED_MONTH[uuid]
        t0 = last_completed_cycles_data["billingStartTs"]
        t1 = last_completed_cycles_data["billingEndTs"]
        api_data_json = api_call(api=DISAGG_DATA_API.format(uuid=uuid, t0=t0, t1=t1), method='GET', params=PARAMS,
                                 data="")

        # by default if appId is not present in last month, it will store default value
        JSON_REPORT[uuid][APPLIANCE_NAME_MAPPING[appId] + "DetectedInItemizationLastMonth"] = "appId " + str(
            appId) + " not present in Itemization"
        for disagg_data in api_data_json:
            if disagg_data["appId"] == appId:
                JSON_REPORT[uuid][APPLIANCE_NAME_MAPPING[appId] + "DetectedInItemizationLastMonth"] = {"appId": appId,
                                                                                                       "value":
                                                                                                           disagg_data[
                                                                                                               "value"]}


# function to get survey details for a user
def get_survey_data(uuid):
    api_data_json = api_call(api=SURVEY_API.format(uuid=uuid), method='GET', params=PARAMS, data="")["payload"][
        "questions"]

    # api_data_json contains list of questions.
    # we need to iterate over all questions to find questions in SURVEY_QUESTION_LIST
    # and answers will be stored in below format
    # JSON_REPORT[uuid]["EVansweredYESInSurvey"]:value
    # JSON_REPORT[uuid]["HeatingAnsweredYESInSurvey"]:value

    for questions in api_data_json:

        # for Q1 (for EV appliance)
        if questions["id"] == SURVEY_QUESTION_LIST[0]:

            # Storing directly whatever the value of the answer chosen for this question for EV in the survey of not None or null

            if questions["answers"] != None:
                JSON_REPORT[uuid]["EVansweredYESInSurvey"] = questions["answers"]
            else:
                JSON_REPORT[uuid]["EVansweredYESInSurvey"] = ""

        # for Q6 (for Heating appliances)
        if questions["id"] == SURVEY_QUESTION_LIST[1]:

            # Storing directly whatever the value of the answer chosen for this question for HEATING in the survey of not None or null

            if questions["answers"] != None:
                JSON_REPORT[uuid]["HeatingAnsweredYESInSurvey"] = questions["answers"]
            else:
                JSON_REPORT[uuid]["HeatingAnsweredYESInSurvey"] = ""


'''
    Below are the helper functions for this script.
'''


# function to calculate start and end timestamp slabs for rate transition users
# currently implemented for 2 continuous calender months
def get_start_end_timeslab_for_rate_transition(rate_effective_timestamp):
    time_slab_list = {}

    if rate_effective_timestamp <= LAST_COMPLETED_CALENDER_START_TIMESTAMP or rate_effective_timestamp >= CURRENT_COMPLETED_CALENDER_END_TIMESTAMP:
        time_slab_list["last_month"] = [
            {"start": LAST_COMPLETED_CALENDER_START_TIMESTAMP, "end": LAST_COMPLETED_CALENDER_END_TIMESTAMP,
             "new_rate_plan_applied": False, "mode": "month"}]
        time_slab_list["current_month"] = [
            {"start": CURRENT_COMPLETED_CALENDER_START_TIMESTAMP, "end": CURRENT_COMPLETED_CALENDER_END_TIMESTAMP,
             "new_rate_plan_applied": False, "mode": "month"}]

    elif rate_effective_timestamp == LAST_COMPLETED_CALENDER_END_TIMESTAMP or rate_effective_timestamp == CURRENT_COMPLETED_CALENDER_START_TIMESTAMP:
        time_slab_list["last_month"] = [
            {"start": LAST_COMPLETED_CALENDER_START_TIMESTAMP, "end": LAST_COMPLETED_CALENDER_END_TIMESTAMP,
             "new_rate_plan_applied": False, "mode": "month"}]
        time_slab_list["current_month"] = [
            {"start": CURRENT_COMPLETED_CALENDER_START_TIMESTAMP, "end": CURRENT_COMPLETED_CALENDER_END_TIMESTAMP,
             "new_rate_plan_applied": True, "mode": "month"}]

    elif rate_effective_timestamp > LAST_COMPLETED_CALENDER_START_TIMESTAMP and rate_effective_timestamp < CURRENT_COMPLETED_CALENDER_START_TIMESTAMP:
        time_slab_list["last_month"] = [
            {"start": LAST_COMPLETED_CALENDER_START_TIMESTAMP, "end": rate_effective_timestamp,
             "new_rate_plan_applied": False, "mode": "day"},
            {"start": rate_effective_timestamp, "end": LAST_COMPLETED_CALENDER_END_TIMESTAMP,
             "new_rate_plan_applied": True, "mode": "day"}]
        time_slab_list["current_month"] = [
            {"start": CURRENT_COMPLETED_CALENDER_START_TIMESTAMP, "end": CURRENT_COMPLETED_CALENDER_END_TIMESTAMP,
             "new_rate_plan_applied": True, "mode": "month"}]

    elif rate_effective_timestamp > CURRENT_COMPLETED_CALENDER_START_TIMESTAMP and rate_effective_timestamp < CURRENT_COMPLETED_CALENDER_END_TIMESTAMP:
        time_slab_list["last_month"] = [
            {"start": LAST_COMPLETED_CALENDER_START_TIMESTAMP, "end": LAST_COMPLETED_CALENDER_END_TIMESTAMP,
             "new_rate_plan_applied": False, "mode": "month"}]
        time_slab_list["current_month"] = [
            {"start": CURRENT_COMPLETED_CALENDER_START_TIMESTAMP, "end": rate_effective_timestamp,
             "new_rate_plan_applied": False, "mode": "day"},
            {"start": rate_effective_timestamp, "end": CURRENT_COMPLETED_CALENDER_END_TIMESTAMP,
             "new_rate_plan_applied": True, "mode": "day"}]

    return time_slab_list


# function to do curd operations(GET,POST,PUT etc)
def api_call(method, api, params, data):
    # api response will be stored in response_json in json format
    response_json = {}

    # for now only implementing GET request as required
    try:
        if method == 'GET':
            response = requests.get(url=api, params=params)
            if response.status_code == 200:
                response_json = response.json()
    except Exception as e:
        print("exception occured while fetching from ", api, "\n", e)

    # logging the api ionformation in logger file
    logging.info(
        "api calling:\n" + " api:" + str(api) + " params:" + str(params) + "\n" + "response:\n" + str(response_json))

    return response_json


# thread target function that will perform all operations for a user using a perticular thread
def thread_target_function(uuid_list, start, end):
    for uuid in uuid_list[start:end + 1]:

        try:
            print("user rate information data is being fetched for user:", uuid)
            get_uuid_rate_info(uuid)
            print("user rate information data fetch completed for user:", uuid)
        except Exception as e:
            print("exception occured while fetching user rate information for user:", uuid)
            print(e)

        try:
            print("user required completed billing cycle data is being fetched for user:", uuid)
            get_completed_billing_cycles(uuid, 2)
            print("user required completed billing cycle data fetch completed for user:", uuid)
        except Exception as e:
            print("exception occured while fetching user required completed billing cycle for user:", uuid)
            print(e)

        try:
            print("user disagg data is being fetched for user:", uuid)
            get_disagg_data(uuid)
            print("user disagg data fetch completed for user:", uuid)
        except Exception as e:
            print("exception occured while fetching user disagg data for user:", uuid)
            print(e)

        try:
            print("user survey data is being fetched for user:", uuid)
            get_survey_data(uuid)
            print("user survey data fetch completed for user:", uuid)
        except Exception as e:
            print("exception occured while fetching user survey data for user:", uuid)
            print(e)

        try:
            print("user billing data is being fetched for user:", uuid)
            get_billing_data_info(uuid=uuid, PlanNumber=JSON_REPORT[uuid]["PlanNumber"])
            print("user billing data fetch completed for user:", uuid)
        except Exception as e:
            print("exception occured while fetching user billing data for user:", uuid)
            print(e)

        print("Data fetching completed for user:", uuid)
        print("Data fetched for user:", uuid, " is:\n", JSON_REPORT[uuid])
        print("thread_target_function for user:", uuid, " completed")


# function to create different sets of uuids(chunks) so as to perform api call on them using multithreading
'''
    # creates start and end indices
    # CHUNK_INDEICES=[{START_INDEX:VALUE,END_INDEX:VALUE},...]
    # end index is exclusive
'''

# function to create different chunk indices for tou and non tou user list or chunks for each thread
# based on the start and end index and the size of each chunk
# indices will be like [{start:value,end:value},...]
CHUNK_INDICES_FOR_TOU = []
CHUNK_INDICES_FOR_NONTOU = []


def create_chunks(start_index, end_index, size):
    chunks = []

    '''
        working algorithm:
        # no_of_chunks_to_be_formed= math.ceil( (end_index - start_index) / (size) )
        # start = start_index,end=start+size
        # next start = end (if next start exceeds end_index then break the loop) , 
        # next end = MIN( start+size , end_index) => this is to restrict end to exceed the end_index
        # chunks.append({start:start,end:end})
        # iterate like this
    '''

    no_of_chunks_to_be_formed = math.floor((end_index - start_index) / (size))
    print("no_of_chunks_to_be_formed:", no_of_chunks_to_be_formed)
    start = start_index
    end = min(start + size, end_index)

    while start <= end and end <= end_index:
        print("start:", start, " end:", end)

        chunks.append({"start": start, "end": end})

        start = end + 1
        if start > end_index:
            break

        end = min(start + size, end_index)

    return chunks


# create different thread sets as per thread limit and execute them parallely via function thread_target_function
# where each thread will handle one uuid and its api calls
def create_and_execute_threads(index_for_threads, uuid_list):
    threads_collection = []
    for index in index_for_threads:
        thread_object = threading.Thread(target=thread_target_function, args=(uuid_list, index["start"], index["end"]))
        threads_collection.append(thread_object)
    print("thread formation done for thread index ", index_for_threads)
    print("starting each thread in thread_collection...")
    for thread in threads_collection:
        thread.start()
    print("joining each thread in thread_collection to main thread...")
    for thread in threads_collection:
        thread.join()
    print("ALL thread functions are executed")


# export JSON data to excel sheet
def export_json_to_excelSheet(uuid_list, user_tier):
    wb = Workbook()
    # add_sheet is used to create sheet.
    sheet = wb.add_sheet(user_tier + '_REPORT')

    # sheet1.write(row,col,data)
    # initializing row and col to 0,0
    row = 0
    col = 0

    # creating sheet Header
    for column_name in SHEET_HEADER_DATA:
        sheet.write(row, col, column_name)
        # incrementing column number
        col += 1

    row += 1
    col = 0
    # writing JSON_REPORT DATA in sheet

    try:
        for uuid in uuid_list:
            sheet.write(row, col, uuid)
            col += 1
            for field_name in SHEET_HEADER_DATA[1:]:
                if uuid in JSON_REPORT.keys():
                    data = str(JSON_REPORT[uuid][field_name])
                else:
                    data = ""
                sheet.write(row, col, data)
                col += 1

            # making column number 0 to start from 0th index for new row
            col = 0
            # incrementing row to write data in next row
            row += 1
            wb.save('/Users/navneetnipu/Desktop/' + user_tier + '_report.xlsx')

    except Exception as e:
        print("exception occured while exporting data to excel for user:", uuid)
        print(e)
    wb.save('/Users/navneetnipu/Desktop/report.xlsx')


if __name__ == '__main__':
    print("Entered into main function...")

    try:
        # logging the user input values to log file

        logging.info("DATA_SERVER_URL:" + DATA_SERVER_URL)
        logging.info("ACCESS_TOKEN:" + ACCESS_TOKEN)
        logging.info("PARAMS:" + str(PARAMS))
        logging.info("NO_OF_THREADS_TO_BE_MADE:" + str(NO_OF_THREADS_TO_BE_MADE))
        logging.info("TOU_CHUNK_SIZE:" + str(TOU_CHUNK_SIZE))
        logging.info("NON_TOU_CHUNK_SIZE:" + str(NON_TOU_CHUNK_SIZE))
        logging.info("TIMEZONE:" + TIMEZONE)
        logging.info("DEFAULT MODE:" + MODE)
        logging.info("HID:" + str(HID))
        logging.info("DEFAULT_T0:" + str(DEFAULT_T0))
        logging.info("DEFAULT_T1:" + str(DEFAULT_T1))
        logging.info("LOCALE:" + LOCALE)
        logging.info("APPLIANCE_ID_LIST:" + str(APPLIANCE_ID_LIST))
        logging.info("SURVEY_QUESTION_LIST:" + str(SURVEY_QUESTION_LIST))
        logging.info("MEASUREMENT_TYPE:" + MEASUREMENT_TYPE)
        logging.info("TOU_FILE_PATH:" + TOU_FILE_PATH)
        logging.info("NONTOU_FILE_PATH:" + NONTOU_FILE_PATH)
        logging.info("APPLIANCE_NAME_MAPPING:" + str(APPLIANCE_NAME_MAPPING))
        logging.info("RATE_PLAN_TO_CATEGORY_MAPPING:" + str(RATE_PLAN_TO_CATEGORY_MAPPING))
        logging.info("RATE_PLAN_MAPPING:" + str(RATE_PLAN_MAPPING))
        logging.info("TIER_PROGRAM_ID:" + TIER_PROGRAM_ID)
        logging.info("TOU_PROGRAM_ID:" + TOU_PROGRAM_ID)
        logging.info("FIND_PROGRAM_ID_FROM_RATE_CATEGORY:" + str(FIND_PROGRAM_ID_FROM_RATE_CATEGORY))
        logging.info("LAST_COMPLETED_CALENDER_START_TIMESTAMP:" + str(LAST_COMPLETED_CALENDER_START_TIMESTAMP))
        logging.info("LAST_COMPLETED_CALENDER_END_TIMESTAMP:" + str(LAST_COMPLETED_CALENDER_END_TIMESTAMP))
        logging.info("CURRENT_COMPLETED_CALENDER_START_TIMESTAMP:" + str(CURRENT_COMPLETED_CALENDER_START_TIMESTAMP))
        logging.info("CURRENT_COMPLETED_CALENDER_END_TIMESTAMP:" + str(CURRENT_COMPLETED_CALENDER_END_TIMESTAMP))
        print("logging user inputs completed")

    except Exception as e:
        print("exception occured while logging data into logger")
        print(e)

    # getting tou uuid list from file
    print("getting uuid list for tou users from file ", TOU_FILE_PATH)
    TOU_UUID = get_uuid_list_from_file(TOU_FILE_PATH)

    # getting nontou uuid list from file
    print("getting uuid list for nontou users from file ", NONTOU_FILE_PATH)
    NON_TOU_UUID = get_uuid_list_from_file(NONTOU_FILE_PATH)

    # creating chunk indices for tou user list
    print("chunk indices formation for TOU users started")
    tou_user_len = len(TOU_UUID)
    CHUNK_INDICES_FOR_TOU = create_chunks(start_index=0, end_index=tou_user_len - 1, size=TOU_CHUNK_SIZE)

    print(CHUNK_INDICES_FOR_TOU)
    print("chunk indices formation for TOU users done")

    # creating chunk indices for non tou user list
    print("chunk indices formation for NONTOU users started")
    nontou_user_len = len(NON_TOU_UUID)
    CHUNK_INDICES_FOR_NONTOU = create_chunks(start_index=0, end_index=nontou_user_len - 1, size=NON_TOU_CHUNK_SIZE)

    print(CHUNK_INDICES_FOR_NONTOU)
    print("chunk indices formation for NONTOU users done")

    # creating chunks for each thread to operate on a single user chunk simultaneoulsy
    # for example, let say single user chunk is of 100 size,and max thread size is 10 then
    # each thread will operate on 10 users so that 10 thread * 10 uuid per thread=100(each chunk size)

    print("thread operation on TOU USERS are started")
    # forming chunk for threads for tou users
    for chunk in CHUNK_INDICES_FOR_TOU:
        chunk_len_for_each_thread = math.ceil(chunk["end"] - chunk["start"]) + 1

        # using min(chunk_len_for_each_thread,NO_OF_THREADS_TO_BE_MADE) because if thread size is more than uuids in 1 chunk then
        # no use of extra threads
        # thread size should be less than or equal to chunk size for each thread
        CHUNK_FOR_EACH_THREADS = create_chunks(start_index=chunk["start"],
                                               end_index=chunk["start"] + chunk_len_for_each_thread - 1,
                                               size=min(chunk_len_for_each_thread, NO_OF_THREADS_TO_BE_MADE))

        print("chunk: ", chunk, " chunk for each thread:", CHUNK_FOR_EACH_THREADS)

        # generating threads for tou users
        create_and_execute_threads(index_for_threads=CHUNK_FOR_EACH_THREADS, uuid_list=TOU_UUID)

    print("thread operation on TOU USERS are completed")

    print("thread operation on NONTOU USERS are started")
    # forming chunk for threads for nontou users
    for chunk in CHUNK_INDICES_FOR_NONTOU:
        chunk_len_for_each_thread = math.ceil(chunk["end"] - chunk["start"]) + 1
        CHUNK_FOR_EACH_THREADS = create_chunks(start_index=chunk["start"],
                                               end_index=chunk["start"] + chunk_len_for_each_thread - 1,
                                               size=min(chunk_len_for_each_thread, NO_OF_THREADS_TO_BE_MADE))

        print("chunk: ", chunk, " chunk for each thread:", CHUNK_FOR_EACH_THREADS)

        # generating threads for non tou users
        create_and_execute_threads(index_for_threads=CHUNK_FOR_EACH_THREADS, uuid_list=NON_TOU_UUID)

    print("thread operation on NONTOU USERS are completed")

    print("JSON_REPORT:\n", JSON_REPORT)
    print(JSON_REPORT.keys())

    print("exporting JSON_REPORT data to excel sheet")

    print("exporting JSON_REPORT data to excel sheet for TOU users")
    export_json_to_excelSheet(uuid_list=TOU_UUID, user_tier="TOU")
    print("exporting of JSON_REPORT data to excel sheet for TOU users done")

    print("exporting JSON_REPORT data to excel sheet for NONTOU users")
    export_json_to_excelSheet(uuid_list=NON_TOU_UUID, user_tier="NON_TOU")
    print("exporting of JSON_REPORT data to excel sheet for NONTOU users done")

    print("data writing to excel done")

    try:
        if os.path.isfile(LOG_FILE_PATH):
            print("log file has been created at path:", LOG_FILE_PATH)
        else:
            print("log file has not been created at path:", LOG_FILE_PATH)
    except Exception as e:
        print("exception occured while reading file from directory :", LOG_FILE_PATH)
        print(e)

    print("code execution completed!")
