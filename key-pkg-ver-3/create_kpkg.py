from utils.create_kpkg_helper import *
from utils.input_utils import *
import pyinputplus as pyip, sys, json, re

def main():
    """Interactive function for creating key packages
    """

    target_list = None
    operation = None
    key_package = None
    key_packages_list = []
    first_user_input = "CREATE A NEW KEY PACKAGE"

    while True:
        if first_user_input == "CREATE A NEW KEY PACKAGE" :
            # create a new key pkg
            target_list = pyip.inputMenu(VALID_TARGET_LIST, numbered = True, prompt = "Please select a target list:\n")
            operation = pyip.inputMenu(VALID_OPERATIONS, numbered = True, prompt = "Please select an operation:\n")
            key_type = pyip.inputMenu(VALID_KEY_TYPES, numbered = True, prompt = "Please select a key type:\n")
            key_name = input_key_name()
            key_metadata = input_key_metadata()
            key_file_content = pyip.inputStr(postValidateApplyFunc=get_file_content, prompt = "Please input key file path:\n")
            while key_file_content is None:
                print("ERROR: Please enter a valid file path.")
                key_file_content = pyip.inputStr(postValidateApplyFunc=get_file_content, prompt = "Please input key file path:\n")
            # create a new key
            key = Key(key_type, key_name, key_file_content, key_metadata)
            if len(key_packages_list) == 0:
                # create a new key package and append to key package list
                key_packages_list.append({"target_list": target_list, "operation": operation, "keys": [key.__dict__]})
            else:
                # check if key package already exist
                is_key_package_found = False
                for key_package in key_packages_list:
                    if key_package["target_list"] == target_list and key_package["operation"] == operation:
                        # key package already exist
                        key_package["keys"].append(key.__dict__)
                        is_key_package_found = True
                        break
                if not is_key_package_found:
                    # create a new key package and append to key package list
                    key_packages_list.append({"target_list": target_list, "operation": operation, "keys": [key.__dict__]})

            first_user_input = pyip.inputMenu(["YES, add more key(s)", "NO"], numbered=True, prompt="Do you want to add more key(s) to this key package?:\n")
            if first_user_input == "YES, add more key(s)":
                continue

        elif first_user_input == 'YES, add more key(s)':
            # continue appending to last key pkg
            # we already have a target_list and an operation
            key_type = pyip.inputMenu(VALID_KEY_TYPES, numbered = True, prompt = "Please select a key type:\n")
            key_name = input_key_name()
            key_metadata = input_key_metadata()
            key_file_content = pyip.inputStr(prompt = "Please input key file path:\n")
            key = Key(key_type, key_name, key_file_content, key_metadata)
            key_packages_list[-1]["keys"].append(key.__dict__)
            first_user_input = pyip.inputMenu(["YES, I want to add more key(s)", "NO"], numbered=True, prompt="Do you want to add more key(s) to this key package?:\n")
            if first_user_input == "YES, add more key(s)":
                continue

        elif first_user_input == 'FINISH AND SAVE OUTPUT FILE':
            save_filename = pyip.inputStr(prompt = "Please input filename for output:\n")
            key_packages_json_obj = json.dumps({"key_packages": key_packages_list}, indent = 4)
            try:
                with open(save_filename, "w") as file_to_write:
                    file_to_write.write(key_packages_json_obj)
            except:
                sys.exit("Couldn't write output to the path provided!")
            print("Saved output in:", save_filename)
            break

        elif first_user_input == "QUIT WITHOUT SAVING":
            print("Quitting without saving...\n")
            break

        first_user_input = pyip.inputMenu(['CREATE A NEW KEY PACKAGE', 'FINISH AND SAVE OUTPUT FILE', 'QUIT WITHOUT SAVING'], numbered = True, prompt = "Please select one of the following options:\n")

    sys.exit(0)


if __name__ == "__main__":
    main()