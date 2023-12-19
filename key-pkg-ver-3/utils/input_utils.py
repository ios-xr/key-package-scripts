# util for helping in input validation
import pyinputplus as pyip, re

MAX_RETRY = 5
MAX_KEY_NAME_LEN = 6
MAX_KEY_METADATA_LEN = 128
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

def input_key_name():
    key_name = None
    max_retry = MAX_RETRY
    while max_retry != 0:
        key_name = pyip.inputStr(blank=True, prompt = "Please input key name:\n")
        is_valid_key_name = validate_key_name(key_name)
        if isinstance(is_valid_key_name, bool) and is_valid_key_name is True:
            return key_name
        else:
            print(is_valid_key_name)
        max_retry = max_retry - 1
        print("Retries left:", max_retry)
    print("Max retry reached!")
    exit(1)


def input_key_metadata():
    key_metadata = None
    max_retry = MAX_RETRY
    while max_retry != 0:
        key_metadata = pyip.inputStr(blank=True, prompt = "Please input key metadata:\n")
        is_valid_key_metadata = validate_key_metadata(key_metadata)
        if isinstance(is_valid_key_metadata, bool) and is_valid_key_metadata is True:
            return key_metadata
        else:
            print(is_valid_key_metadata)
        max_retry = max_retry - 1
        print("Retries left:", max_retry)
    print("Max retry reached!")
    exit(1)