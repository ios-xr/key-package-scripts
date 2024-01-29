# util for helping in input validation
import pyinputplus as pyip, re
from datetime import datetime

MAX_KEY_NAME_LEN = 6
MAX_KEY_METADATA_LEN = 128
TIMESTAMP_LEN = 41
VALID_TARGET_LIST = ['ALLOWED_LIST','REVOKED_LIST']
VALID_OPERATIONS = ['APPEND','DELETE', 'REPLACE']
VALID_KEY_TYPES = ['X509KEY','GPGKEY']


def validate_key_name(key_name):
    if re.search(r'[^A-Za-z0-9_-]', key_name):
        return "Only - , _ and alphanumeric char allowed in key name"
    if len(key_name) > MAX_KEY_NAME_LEN:
        return "key name length cannot be more than 6 characters"
    return True


def validate_key_metadata(key_metadata):
    if re.search(r'[^A-Za-z0-9_-]', key_metadata):
        return "Only - , _ and alphanumeric char allowed in key metadata"
    if len(key_metadata) > MAX_KEY_METADATA_LEN:
        return "key name length cannot be more than 128 characters"
    return True


def validate_timestamp(timestamp):
    if timestamp == "":
        return True
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


def input_key_name():
    key_name = None
    while True:
        key_name = pyip.inputStr(blank=True, prompt = "Please input key name:\n")
        is_valid_key_name = validate_key_name(key_name)
        if isinstance(is_valid_key_name, bool) and is_valid_key_name is True:
            return key_name
        else:
            print(is_valid_key_name)
        print("Please retry with a valid input.")


def input_key_metadata():
    key_metadata = None
    while True:
        key_metadata = pyip.inputStr(blank=True, prompt = "Please input key metadata:\n")
        is_valid_key_metadata = validate_key_metadata(key_metadata)
        if isinstance(is_valid_key_metadata, bool) and is_valid_key_metadata is True:
            return key_metadata
        else:
            print(is_valid_key_metadata)
        print("Please retry with a valid input.")

def input_timestamp():
    timestamp = None
    while True:
        timestamp = pyip.inputStr(blank=True, prompt = "Please input timestamp (in 'date -R' format):\n")
        is_valid_timestamp = validate_timestamp(timestamp)
        if isinstance(is_valid_timestamp, bool) and is_valid_timestamp is True:
            return timestamp
        else:
            print(is_valid_timestamp)
        print("Please retry with a valid input.")