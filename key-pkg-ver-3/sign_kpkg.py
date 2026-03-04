import argparse
import json
import sys
import subprocess
from utils.create_kpkg_helper import *
from utils.input_utils import *

TEMP_CONFIG_FILE_WITH_TIMESTAMP = 'modified_config_with_ts.json'

def add_timestamp(config_file_input_path, timestamp):
    '''Add timestamp, if timestamp value is blank, generate and add.
    Expects a valid timestamp or blank timestamp value
    '''
    with open(config_file_input_path, 'r') as new_config_file:
        config_file_data = json.load(new_config_file)
        if not timestamp:
            timestamp = subprocess.check_output(['date', '-R']).decode().strip()
        config_file_data['timestamp'] = timestamp

    with open(TEMP_CONFIG_FILE_WITH_TIMESTAMP, 'w') as modified_config_file:
        json.dump(config_file_data, modified_config_file, indent=4)

    return TEMP_CONFIG_FILE_WITH_TIMESTAMP

def main():
    parser = argparse.ArgumentParser(description="Sign key package config file.")
    parser.add_argument('-A', '--allowed', required=False, help="Comma-separated list of allowed key package JSON files")
    parser.add_argument('-R', '--revoked', required=False, help="Comma-separated list of revoked key package JSON files")
    parser.add_argument('-p', '--pub_cert', required=True, help="Ownership cert file")
    parser.add_argument('-r', '--priv_key', required=True, help="Ownership private key file")
    parser.add_argument('-o', '--output_file', required=True, help="Output file name")
    parser.add_argument('-t', '--timestamp', help="Timestamp (in 'date -R' output format), if not provided, current system's timestamp will be used")
    parser.add_argument('-n', '--nosign', required=False, action='store_true',
                        help="Generate key package but don't sign.")

    args = parser.parse_args()

    if not args.allowed and not args.revoked:
        print("At least one of allowed or revoked key packages should be provided.")
        sys.exit(1)
    
    # Combine allowed and revoked key packages
    key_packages = {VERSION_STR: VERSION, TIMESTAMP_STR: "", OPERATION_STR: UPDATE_STR}

    allowed_files = []
    revoked_files = []
    if args.allowed:
        key_packages[ALLOWED_LIST_STR] = []
        allowed_files = args.allowed.split(',')
        for file in allowed_files:
            if not validate_key_package(file):
                sys.exit(1)
    
    if args.revoked:
        key_packages[REVOKED_LIST_STR] = []
        revoked_files = args.revoked.split(',')
        for file in revoked_files:
            if not validate_key_package(file):
                sys.exit(1)
   
    pub_cert = args.pub_cert
    priv_key = args.priv_key
    output_file = args.output_file
    timestamp = args.timestamp

    for file in allowed_files:
        if os.path.getsize(file) == 0:
            continue
        with open(file, 'r') as f:
            key_packages[ALLOWED_LIST_STR].append(json.load(f))

    for file in revoked_files:
        if os.path.getsize(file) == 0:
            continue
        with open(file, 'r') as f:
            key_packages[REVOKED_LIST_STR].append(json.load(f))

    # If timestamp is provided, add it with TIMESTAMP key after validating
    if timestamp:
        is_valid_timestamp = validate_timestamp(timestamp)
        if not is_valid_timestamp:
            print("Invalid timestamp provided. Exiting.")
            sys.exit(1)

        key_packages[TIMESTAMP_STR] = timestamp
    else:
        try:
            key_packages[TIMESTAMP_STR] = subprocess.check_output(['date', '-R']).decode().strip()
        except Exception as e:
            print(f"Error on getting time: {e}")
            sys.exit(1)

    if args.nosign:
        with open(output_file, 'w') as f:
            json.dump(key_packages, f, indent=4)
        print(f"Unsigned key package saved to: {output_file}")
        sys.exit(0)
    
    # Write combined key packages to a temporary file
    kpkg_json_file = 'unsigned_kpkg.json'
    with open(kpkg_json_file, 'w') as f:
        json.dump(key_packages, f, indent=4)

    print("Signing key package...")
    ret_code = 0
    # Sign the final config file
    sign_cmd = f"openssl smime -sign -binary -in {kpkg_json_file} -signer {pub_cert} -inkey {priv_key} -outform DER -nodetach -out {output_file}"

    try:
        subprocess.run(sign_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing sign command: {e}")
        ret_code = 1
    

    print(f"Signed key package saved to: {output_file}")
    sys.exit(ret_code)

if __name__ == "__main__":
    main()