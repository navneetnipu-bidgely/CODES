import json

import requests

# json file from launchpad
SRC_JSON_FILE_PATH="/Users/navneetnipu/Desktop/src_json_file.json"

# SRC_JSON_FILE_PATH file format
# val={"CONFIG_STD":
#     [
#     {
#       "entity": "PILOT",
#       "entityId": "10084",
#       "params": {
#         "PILOT_ID": "10084"
#       },
#     "request": [ {
#           "payload": {
#             "key": "delivery_modes",
#             "configType": "event_subscriptions.USER_WELCOME.GAS",
#             "val": "[]",
#             "documentation": "TODO",
#             "regex": ".*",
#             "tags": [],
#             "components": [
#               "PROJECT_LEVEL_CONFIGURATIONS"
#             ],
#             "dataType": "TEXT"
#           },
#           "supportedEnvs": [
#             "prod-na-2",
#             "nonprodqa",
#             "uat"
#           ]
#         }
#     ]
#     }
#     ]
# }

# json file from environment
DEST_JSON_FILE_PATH="/Users/navneetnipu/Desktop/dest_json_file.json"

# DEST_JSON_FILE_PATH file format
# val={
#     "email_picture_greeting_section_configs":
#         "{\"kvs\":[{\"key\":\"greeting_heading_text\",\"val\":\"com.bidgely.cloud.pictureGreeting.heading.text\",\"version\":2,\"lastUpdatedTimestamp\":1678965305}]}"
# }


with open(SRC_JSON_FILE_PATH) as f:
    # Load the JSON data into a Python object
    data = json.load(f)
    src_config_data_list = data["CONFIG_STD"][0]["request"]

# getting dest config data from api
api="https://gpcsmbuatapi.bidgely.com/entities/pilot/10084.MONTHLY_SUMMARY.ELECTRIC/configs/"
params={"access_token":"56b02db5-b83c-4c5c-b75d-3b6eaee03438"}
response = requests.get(url=api, params=params)
if response.status_code == 200:
    response_json = response.json()

dest_config_json_data=response_json

# with open(DEST_JSON_FILE_PATH) as f:
#     # Load the JSON data into a Python object
#     dest_config_json_data = json.load(f)



# create a configs json file from SRC_JSON_FILE_PATH file where key should be present
# in DEST_JSON_FILE_PATH file


CONFIG_TYPES_IN_PR=[]
CONFIG_TYPE_KEY_IN_PR={}

FINAL_CONFIG_DATA=[]

MISSING_CONFIGS_DATA_JSON=[]

for config_data in src_config_data_list:
    config_type=config_data["payload"]["configType"]
    config_key=config_data["payload"]["key"]
    CONFIG_TYPE_KEY_IN_PR[config_type+"|"+config_key]=1
    CONFIG_TYPES_IN_PR.append(config_type)
    if config_type in dest_config_json_data:
        dest_config_keys_list=json.loads(dest_config_json_data[config_type])["kvs"]
        for config_key_data in dest_config_keys_list:
            if config_key==config_key_data["key"]:
                # print(config_key)
                FINAL_CONFIG_DATA.append(config_data)
                break
    else:
        with open('/Users/navneetnipu/Desktop/extra_config_in_launchpad_pr.txt', 'a') as f:
            # Write the JSON data to the file
            f.write(config_type+" , "+config_key+"\n")

FINAL_CONFIG_JSON_DATA={"CONFIG_STD":[
    {"entity": "PILOT",
      "entityId": "10084",
      "params": {
        "PILOT_ID": "10084"
      },"request": FINAL_CONFIG_DATA
     }
]
}

with open('/Users/navneetnipu/Desktop/final_config_json_file.json', 'w') as f:
    # Write the JSON data to the file
    json.dump(FINAL_CONFIG_JSON_DATA, f)


CONFIG_TYPES_IN_PR_SET=set(CONFIG_TYPES_IN_PR)
# print(CONFIG_TYPES_IN_PR)

print(CONFIG_TYPES_IN_PR_SET)

for config_type in dest_config_json_data:
    config_keys_list=json.loads(dest_config_json_data[config_type])["kvs"]
    for config_key in config_keys_list:
        key=str(config_type)+"|"+str(config_key["key"])
        if config_type in CONFIG_TYPES_IN_PR_SET :
            if key not in CONFIG_TYPE_KEY_IN_PR:
                MISSING_CONFIGS_DATA_JSON.append(key)
                with open('/Users/navneetnipu/Desktop/configs_missing_in_launchpad_pr.txt', 'a') as f:
                    f.write(key+"\n")


# print(MISSING_CONFIGS_DATA_JSON)
