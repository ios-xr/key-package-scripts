import json, argparse
from utils.create_kpkg_helper import *
from utils.input_utils import *


def key_dict_validator(key_dict):
    # print("key_dict_validator:::")
    '''Return True only if valid, otherwise return error string
    '''
    if len(list(key_dict.keys())) == 4:
        key_dict_keys_list =  list(key_dict.keys())
        if "key_type" in key_dict_keys_list and "key_name" in key_dict_keys_list and "key_metadata" in key_dict_keys_list and "key_value" in key_dict_keys_list:
            if key_dict["key_type"] not in ['X509KEY','GPGKEY']:
                return '"key_type" is invalid'
            is_valid_key_name = validate_key_name(key_dict["key_name"])
            if isinstance(is_valid_key_name, bool) is False or is_valid_key_name is False:
                return is_valid_key_name
            is_valid_key_metadata = validate_key_metadata(key_dict["key_metadata"])
            if isinstance(is_valid_key_metadata, bool) is not True or is_valid_key_metadata is not True:
                return is_valid_key_metadata
            if len(key_dict['key_metadata']) > 128:
                return'"key_metadata" value cannot be more than 128 characters!'
            return True
    return 'Some key details are incorrect!'


def kpkg_dict_validator(key_package_dict):
    # print("kpkg_dict_validator:::")
    '''Return True only if valid, otherwise return error string
    '''
    if len(list(key_package_dict.keys())) == 3:
        key_package_dict_keys_list = list(key_package_dict.keys())
        if "target_list" in key_package_dict_keys_list and "operation" in key_package_dict_keys_list and "keys" in key_package_dict_keys_list:
            if key_package_dict["target_list"] not in ['ALLOWED_LIST','REVOKED_LIST']:
                return '"target_list" value is invalid'
            if key_package_dict["operation"] not in ['APPEND','DELETE', 'REPLACE']:
                return '"operation" value is invalid'
            if len(key_package_dict["keys"]) == 0:
                return '"keys" should have at least one key!'
            if isinstance(key_package_dict["keys"], list) is False:
                return '"keys" value is not a type of list'
            for key_dict in key_package_dict["keys"]:
                if key_dict_validator(key_dict) is not True:
                    return key_dict_validator(key_dict)
            return True
    return 'Some key package details are incorrect!'


def kpkg_config_validator(kpkg_config_dict):
    # print("kpkg_config_validator:::")
    # check if only one top key named as "key_packages"
    # print(type(kpkg_dict.keys()))
    if len(list(kpkg_config_dict.keys())) == 1 and list(kpkg_config_dict.keys())[0] == "key_packages":
        # check if "key_packages" key is having value of type list
        if isinstance(kpkg_config_dict["key_packages"], list):
            # for each "key_package" value, check if it is a valid kpkg
            if len(kpkg_config_dict["key_packages"]) == 0:
                return '"key_packages" should have at least one key package!'
            for key_package_dict in kpkg_config_dict["key_packages"]:
                is_kpkg_dict_correct = kpkg_dict_validator(key_package_dict)
                if is_kpkg_dict_correct is not True:
                    return is_kpkg_dict_correct
            return True
        else:
            return '"key_package" value is not a type of list'
    else:
        return '"key_packages" key in json, is in incorrect format'


def validate_kpkg(kpkg_config_file_path):
    kpkg_file_content = get_file_content(kpkg_config_file_path)
    try:
        kpkg_config_dict = json.loads(kpkg_file_content)
        is_valid_kpkg = kpkg_config_validator(kpkg_config_dict)
        if is_valid_kpkg is True:
            print("Key Package is valid")
        else:
            print("Key package is invalid!")
            print(is_valid_kpkg)
            exit(1)
    except Exception as e:
        print("Input key package json file format is incorrect!\n")
        exit(1)


def input_and_validate_kpkg():
    parser = argparse.ArgumentParser(description = "Validate a manually created key package .json file")
    parser.add_argument('-f', '--keypackage', required=True, help="Path to Key package json file to be validated")
    args = parser.parse_args()

    kpkg_content = get_file_content(args.keypackage)
    if kpkg_content is  None:
        print("Key package file path is invalid!")
    else:
        try:
            kpkg_config_dict = json.loads(kpkg_content)
            is_valid_kpkg = kpkg_config_validator(kpkg_config_dict)
            if is_valid_kpkg is True:
                print("Key Package is valid")
            else:
                print("Key package is invalid!")
                print(is_valid_kpkg)
        except Exception as e:
            print("Input key package json file format is incorrect!\n")


def main():
    input_and_validate_kpkg()

if __name__ == "__main__":
    main()