import argparse
import json
import sys
from utils.input_utils import *

def main():
    parser = argparse.ArgumentParser(description="Create signed key package file")
    parser.add_argument('-u', '--key_name', required=True, help="Name of the keys")
    parser.add_argument('-k', '--key_type', required=True, choices=['GPG', 'X509'], help="Type of key")
    parser.add_argument('-i', '--key_file', required=True, help="File containing the key content")
    parser.add_argument('-f', '--output_file', required=True, help="Output file")
    
    args = parser.parse_args()

    key_name = args.key_name
    key_type = args.key_type
    key_file_path = args.key_file
    output_file = args.output_file

    key_file_content = get_file_content(key_file_path)
    if key_file_content is None:
        sys.exit(f"Failed to read file {key_file_path}. Please enter a valid key file path.")

    ret = validate_key_name(key_name)
    if ret != True:
        print(ret)
        sys.exit(1)

    ret = validate_key_type(key_type)
    if ret != True:
        print(ret)
        sys.exit(1)
                 
    key = Key(key_type, key_name, key_file_content)
    key_package = {
        k.upper(): v for k, v in key.__dict__.items()
    }

    key_packages_json_obj = json.dumps(key_package, indent=4)

    try:
        with open(output_file, "w") as file_to_write:
            file_to_write.write(key_packages_json_obj)
    except:
        sys.exit("Couldn't write output to the path provided!")

    print("Saved output in:", output_file)
    sys.exit(0)


if __name__ == "__main__":
    main()