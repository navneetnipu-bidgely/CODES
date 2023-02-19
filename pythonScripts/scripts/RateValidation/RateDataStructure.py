import calendar
from datetime import datetime

"""
    RATE_PLAN_DATA_STRUCTURE[unique_key]={
        'january':{
            'present':False/True,
            'week_days':{
                        'Monday':False/True,
                        ...
            },
            'days':{
                1:{
                    'present':False/True,
                    'hours':{
                        0:False,
                        1:False,
                        ...
                        },
                2:{...},
                ...
                31:{...}
                }
            }
        }
    }
"""

# current year
CURRENT_YEAR = datetime.now().year

# month number to month name mapping
MONTH_NUMBER_NAME_MAP={
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}

# week days number to name mapping
WEEK_DAYS_NUMBER_NAME_MAP={
     1: 'Monday',
    2: 'Tuesday',
    3: 'Wednesday',
    4: 'Thursday',
    5: 'Friday',
    6: 'Saturday',
    7: 'Sunday'
}

# dict initialization for hours
HOURS_DICT_INITIALIZATION={}

for hour in range(0,24):
    HOURS_DICT_INITIALIZATION[hour]:False

# json initialization for week days
WEEK_DAYS_JSON_INITIALIZATION={
    'Monday':False,
    'Tuesday':False,
    'Wednesday':False,
    'Thursday':False,
    'Friday':False,
    'Saturday':False,
    'Sunday':False
}

RATE_PLAN_DATA_STRUCTURE = {}

for month_number in MONTH_NUMBER_NAME_MAP:
    RATE_PLAN_DATA_STRUCTURE[MONTH_NUMBER_NAME_MAP[month_number]]={
        'present':False,
        'week_days': WEEK_DAYS_JSON_INITIALIZATION,
        'days':{}
    }

for month_number in MONTH_NUMBER_NAME_MAP:
    for day in range(1,32) :
        RATE_PLAN_DATA_STRUCTURE[MONTH_NUMBER_NAME_MAP[month_number]]['days'][day]={
            'present': False,
            'hours': HOURS_DICT_INITIALIZATION,
        }