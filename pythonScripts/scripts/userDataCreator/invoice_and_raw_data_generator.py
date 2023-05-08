# starting epoch timestamp
import calendar
from datetime import datetime
import random

# generates raw and invoice data and populate them in respective files
def create_raw_and_invoice_data(meter_info,epoch_start,epoch_end):

    # start and end epoch times
    EPOCH_START=epoch_start
    EPOCH_END=epoch_end

    # raw data granularity
    RAW_DATA_GRANULARITY=1800
    # rate to calculate cost for invoice from raw data consumption over the billing cycle
    RATE=5

    # invoice and raw file paths
    INVOICE_FILE_PATH="/Users/navneetnipu/Desktop/GPCSMB/test_users/INVOICE_D.txt"
    RAW_FILE_PATH="/Users/navneetnipu/Desktop/GPCSMB/test_users/RAW_D_1800_S.txt"

    # billing cycles
    BC_SCHEDULES=[{"start":"2021-12-01","end":"2022-01-01"},{"start":"2022-01-01","end":"2022-02-01"},{"start":"2022-02-01","end":"2022-03-01"},{"start":"2022-03-01","end":"2022-04-01"},{"start":"2022-04-01","end":"2022-05-01"},{"start":"2022-05-01","end":"2022-06-01"},{"start":"2022-06-01","end":"2022-07-01"},{"start":"2022-07-01","end":"2022-08-01"},{"start":"2022-08-01","end":"2022-09-01"},{"start":"2022-09-01","end":"2022-10-01"},{"start":"2022-10-01","end":"2022-11-01"},{"start":"2022-11-01","end":"2022-12-01"},{"start":"2022-12-01","end":"2023-01-01"},{"start":"2023-01-01","end":"2023-02-01"},{"start":"2023-02-01","end":"2023-03-01"},{"start":"2023-03-01","end":"2023-04-01"},{"start":"2023-04-01","end":"2023-05-01"}]


    # for data quality issue check
    RAW_CONSUMPTION_DATA_PER_DAY={}
    RAW_CONSUMPTION_DATA_PER_BC=[]

    epoch=EPOCH_START
    # generating txt file containing raw data
    with open(RAW_FILE_PATH, "a") as outfile:
        while epoch <= EPOCH_END:

            usage=random.uniform(0.0,1.0).__round__(2)

            epoc_timestamp=datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %I:%M:%S %p')

            # preparing raw data
            raw_data = meter_info + "|"+ epoc_timestamp + "|" + str(usage) + "|0|0"

            outfile.write(raw_data)
            outfile.write('\n')


            date = datetime.fromtimestamp(epoch).strftime('%Y-%m-%d')

            if date not in RAW_CONSUMPTION_DATA_PER_DAY:
                RAW_CONSUMPTION_DATA_PER_DAY[date]=[]

            if date in RAW_CONSUMPTION_DATA_PER_DAY:
                RAW_CONSUMPTION_DATA_PER_DAY[date].append(usage)


            # increamenting timestamp as per RAW_DATA_GRANULARITY
            epoch = epoch + RAW_DATA_GRANULARITY
        outfile.write('\n')

    # aggregating raw data per day for per BC

    for billing_cycle in BC_SCHEDULES:

        consumtion_per_BC = 0

        start_date=billing_cycle["start"]
        start_timestamp=datetime.strptime(start_date, '%Y-%m-%d').timestamp()
        end_date=billing_cycle["end"]
        end_timestamp=datetime.strptime(end_date, '%Y-%m-%d').timestamp()

        for date in RAW_CONSUMPTION_DATA_PER_DAY:
            raw_day_timestamp=datetime.strptime(date, '%Y-%m-%d').timestamp()

            if raw_day_timestamp>=start_timestamp and raw_day_timestamp<end_timestamp:
                for consumption_data_per_granularity in RAW_CONSUMPTION_DATA_PER_DAY[date]:
                    consumtion_per_BC+=consumption_data_per_granularity

        RAW_CONSUMPTION_DATA_PER_BC.append({"bc_start":start_date,"bc_end":end_date,"consumption":consumtion_per_BC.__round__(2)})


    with open(INVOICE_FILE_PATH, "a") as outfile:

            for data in RAW_CONSUMPTION_DATA_PER_BC[:-1]:
                bc_start=data["bc_start"]
                bc_end=data["bc_end"]
                invoice_duration=str((datetime.strptime(bc_end, "%Y-%m-%d")-datetime.strptime(bc_start, "%Y-%m-%d")).days)
                consumption=data["consumption"]
                cost=int(consumption/RATE)

                invoice_data = meter_info+"|ELECTRIC|0|"+bc_start+"|"+bc_end+"|"+invoice_duration+"|TOT KWH|CONSUMPTION_BASED|"+str(consumption)+"|"+str(cost)+"|AMI||"
                outfile.write(invoice_data)
                outfile.write('\n')

    # print("RAW_CONSUMPTION_DATA_PER_DAY:")
    # print(RAW_CONSUMPTION_DATA_PER_DAY)
    # print("RAW_CONSUMPTION_DATA_PER_BC:")
    # print(RAW_CONSUMPTION_DATA_PER_BC)