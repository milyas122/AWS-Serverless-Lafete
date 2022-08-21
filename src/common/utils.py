import pytz
from time import gmtime, strftime
from datetime import datetime

tz_PAK = pytz.timezone('Asia/Karachi')
datetime_PAK = datetime.now(tz_PAK)




def get_current_date_object():
    return datetime_PAK


def get_current_date_time():
    return datetime_PAK.strftime("%Y-%m-%dT%H:%M")


def get_timeStamp():
    return datetime.now(tz_PAK).strftime('%Y-%m-%dT%H:%M:%S')

def get_current_date():
    return datetime_PAK.strftime("%Y-%m-%d")

def get_current_time():
    return datetime_PAK.strftime("%H:%M")

def current_hour():
    return datetime_PAK.strftime("%H")






"""
Route: patients/appointments 
Method: POST
Authorizer Required: Yes
Lambda Name: getAppointmentsFunction
Services: Patient
Unit Test:  
"""
