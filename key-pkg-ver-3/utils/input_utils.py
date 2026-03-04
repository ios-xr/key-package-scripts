# util for helping in input validation
import re
from datetime import datetime
import json
import os

VERSION_STR = "VERSION"
VERSION = 2

TIMESTAMP_STR = "TIMESTAMP"
OPERATION_STR = "OPERATION"
ALLOWED_LIST_STR = "ALLOWED_LIST"
REVOKED_LIST_STR = "REVOKED_LIST"
KEY_STR = "KEY"
UPDATE_STR = "UPDATE"
X509KEY_STR = "X509"
GPGKEY_STR = "GPG"

MAX_KEY_NAME_LEN = 9 
TIMESTAMP_LEN = 41
VALID_TARGET_LIST = [ALLOWED_LIST_STR, REVOKED_LIST_STR]
VALID_OPERATIONS = [UPDATE_STR]
VALID_KEY_TYPES = [X509KEY_STR, GPGKEY_STR]

class Key:
    def __init__(self, key_type, key_name, key_file_content):
        self.key_type = key_type  # can't be empty
        self.key_name = key_name  # can't be empty
        self.key_value = key_file_content


def get_file_content(key_file_path):
    is_file = os.path.isfile(key_file_path)
    if not is_file:
        return None
    try:
        with open(key_file_path) as key_file:
            key_file_content = key_file.read()
            return key_file_content
    except FileNotFoundError:
        # raise Exception("Unable to read the file!")
        return None

# Validate the key package file
def validate_key_package(file):
    try:
        if os.path.getsize(file) == 0:
            return True         # Empty file for clearing the target
        with open(file, 'r') as f:
            key = json.load(f)
    except Exception as e:
        print(f"Error reading key package file: {e}")
        return False
    
    if not key:
        return True
    
    temp_key = Key("", "", "")
   
    for k, _ in temp_key.__dict__.items():
        if k.upper() not in key:
            print(f"Invalid key package file. {k.upper()} not present")
            return False

        if not key.get(k.upper()):
            print(f"Invalid key package file. {k.upper()} is empty")
            return False

    ret = validate_key_name(key["KEY_NAME"])
    if ret != True:
        print(ret)
        return False
    
    ret = validate_key_type(key["KEY_TYPE"])
    if ret != True:
        print(ret)
        return False
    
    return True

def validate_key_type(key_type):
    if key_type not in VALID_KEY_TYPES:
        return f"Invalid key type. Key type should be one of {VALID_KEY_TYPES}"
    return True

def validate_key_name(key_name):
    if key_name == "-AL--" or key_name == "_RV__":     
        return "Invalid key name. Key name can't be -AL-- or _RV__"
    if re.search(r'[^A-Za-z0-9_-]', key_name):
        return "Only - , _ and alphanumeric char allowed in key name"
    if len(key_name) > MAX_KEY_NAME_LEN:
        return f"key name length cannot be more than {MAX_KEY_NAME_LEN} characters"
    return True

def validate_timestamp(timestamp):
    try:
        datetime_obj = datetime.strptime(timestamp[0:(len(timestamp) - 5)],
                                    "%a, %d %b %Y %H:%M:%S ")
    except ValueError as v:
        return('Invalid timestamp provided. Timestamp should be output of \"date -R\"')
    if (datetime_obj.year < 2000) or (datetime_obj.year > 2100):
        return("Invalid YEAR in timestamp. Should be between 2000 and 2100")
    if len(timestamp) > TIMESTAMP_LEN:
        return(f"Length of provided timestamp exceeds limit of {TIMESTAMP_LEN} chars.")
    return True
