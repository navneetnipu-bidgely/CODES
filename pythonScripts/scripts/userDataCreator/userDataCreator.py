import datetime
import random

from pythonScripts.scripts.userDataCreator.invoice_and_raw_data_generator import create_raw_and_invoice_data


def create_raw_and_invoice_files(meter_info,epoch_start,epoch_end):
    create_raw_and_invoice_data(meter_info,epoch_start,epoch_end)


def create_userenroll_data(user_info,extra_user_info):
    user = user_info + extra_user_info
    return user

def create_file(data,file_name):
    with open(file_name, "w") as outfile:
            outfile.write(data)
    outfile.close()

def create_meter_data(meter_info,extra_meter_info):
    meter=meter_info+extra_meter_info
    return meter


if __name__=='__main__':

    user_list=""
    meter_list=""

    METER_FILE_PATH="/Users/navneetnipu/Desktop/GPCSMB/test_users/METERENROLL_30users.txt"
    USERENROLL_FILE_PATH="/Users/navneetnipu/Desktop/GPCSMB/test_users/USERENROLL_30users.txt"

    # epoch start and end fopr raw data generation
    EPOCH_START = 1638297000
    EPOCH_END = 1681886147


    user_count=0
    user_limit=30

    BC_SCHEDULES = [{"start": "2021-12-01", "end": "2022-01-01"}, {"start": "2022-01-01", "end": "2022-02-01"},
                    {"start": "2022-02-01", "end": "2022-03-01"}, {"start": "2022-03-01", "end": "2022-04-01"},
                    {"start": "2022-04-01", "end": "2022-05-01"}, {"start": "2022-05-01", "end": "2022-06-01"},
                    {"start": "2022-06-01", "end": "2022-07-01"}, {"start": "2022-07-01", "end": "2022-08-01"},
                    {"start": "2022-08-01", "end": "2022-09-01"}, {"start": "2022-09-01", "end": "2022-10-01"},
                    {"start": "2022-10-01", "end": "2022-11-01"}, {"start": "2022-11-01", "end": "2022-12-01"},
                    {"start": "2022-12-01", "end": "2023-01-01"}, {"start": "2023-01-01", "end": "2023-02-01"},
                    {"start": "2023-02-01", "end": "2023-03-01"}, {"start": "2023-03-01", "end": "2023-04-01"},
                    {"start": "2023-04-01", "end": "2023-05-01"}]



    account_id="test_account_id"
    customer_id="test_customer_id"
    premise_id="test_premise_id"
    meter_id="test_meter_id"

    extra_user_info="|SMB|navneetnipu@bidgely.com|navneet|nipu|52 1ST AVE E||||HAZLEHURST|GA|31539||PO BOX 1777||||HAZLEHURST|GA|31539|912-375-5494|HOME|EN|OBTAINED|0|"
    extra_meter_info="|ELECTRIC|2014-12-31|9999-12-31||2014-12-31|0|2014-12-31|0|AMI||"

    for id in range(101,131):
        account_val=account_id+str(id)
        customer_val=customer_id+str(id)
        premise_val=premise_id+str(id)
        meter_val=meter_id+str(id)

        user_info=account_val+"|"+customer_val+"|"+premise_val
        meter_info=user_info+"|"+meter_val

        user=create_userenroll_data(user_info,extra_user_info)
        meter=create_meter_data(meter_info,extra_meter_info)

        user_list=user_list+"\n"+user
        meter_list=meter_list+"\n"+meter


        # print(user)
        # print(meter)

        create_raw_and_invoice_files(meter_info,EPOCH_START,EPOCH_END)

    create_file(user_list,USERENROLL_FILE_PATH)
    create_file(meter_list,METER_FILE_PATH)
