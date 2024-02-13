import pyinputplus as pyip
import subprocess, json, os

from utils.create_kpkg_helper import *
from utils.input_utils import *
from validate_kpkg import *

TEMP_CONFIG_FILE_WITH_TIMESTAMP = 'modified_config_with_ts.json'


def add_timestamp(config_file_input_path, timestamp):
    '''Add timestamp, if timestamp value is blank, generate and add
    Expects a valid timestamp or blank timestamp value
    '''

    with open(config_file_input_path, 'r') as new_config_file:
        # read
        config_file_data = json.load(new_config_file)
        # get current timestamp if not provide by user
        if timestamp == "" or timestamp is None:
            cmd_result = subprocess.run(["date", "-R"], stdout=subprocess.PIPE)
            if cmd_result.returncode != 0:
                    print("Failed to get timestamp from system")
                    print("Signing failed!")
                    exit(1)
            else:
                timestamp = (cmd_result.stdout.decode("utf-8")).strip()
        # add timestamp
        config_file_data["timestamp"] = timestamp
        new_config_file_data = json.dumps(config_file_data, indent=4)

    # open
    with open(TEMP_CONFIG_FILE_WITH_TIMESTAMP, 'w') as new_config_file:
        # write
        # print("new_config_file_data#######", new_config_file_data)
        new_config_file.write(new_config_file_data)


def sign_kpkg(public_key_file_path, private_key_file_path, config_input_path, output_path):
    '''Signs a json config file
    pub_key: oc-single.pem, priv_key: oc-single-priv.key, config_file: json config file, output_path: .del file
    '''
    try:
        cmd_result = subprocess.run(["openssl", "smime", "-sign", "-binary", "-in", config_input_path, "-signer", public_key_file_path, "-outform", "DER", "-inkey", private_key_file_path, "-nodetach", "-out",  output_path], stdout=subprocess.PIPE)
        if cmd_result.returncode != 0:
            # print("ERROR:\n",cmd_result.stdout.decode("utf-8"))
            print("Signing failed!")
        else:
            print("Signed Successfully!")
    except Exception as e:
        print("Could not sign due to following reason:")
        print(e)
    finally:
        if os.path.exists(TEMP_CONFIG_FILE_WITH_TIMESTAMP):
            os.remove(TEMP_CONFIG_FILE_WITH_TIMESTAMP)


def main():
    public_key_file_path = pyip.inputStr(prompt = "Please input public key file path:\n")
    while not os.path.isfile(public_key_file_path):
        print("ERROR: Please enter a valid file path.")
        public_key_file_path = pyip.inputStr(prompt = "Please input public key file path:\n")

    private_key_file_path = pyip.inputStr(prompt = "Please input private key file path:\n")
    while not os.path.isfile(private_key_file_path):
        print("ERROR: Please enter a valid file path.")
        private_key_file_path = pyip.inputStr(prompt = "Please input private key file path:\n")

    kpkg_config_file_input_path = pyip.inputStr(prompt = "Please input key package config file path to be signed:\n")
    while not os.path.isfile(kpkg_config_file_input_path):
        print("ERROR: Please enter a valid file path.")
        kpkg_config_file_input_path = pyip.inputStr(prompt = "Please input key package config file path to be signed:\n")

    validate_kpkg(kpkg_config_file_input_path)
    timestamp = input_timestamp()
    output_path = pyip.inputStr(prompt = "Please input filename for output:\n")
    try:
        add_timestamp(kpkg_config_file_input_path, timestamp)
    except Exception as e:
        print("Couldn't add timestamp to config file!")
    else:
        sign_kpkg(public_key_file_path, private_key_file_path, TEMP_CONFIG_FILE_WITH_TIMESTAMP, output_path)
    finally:
        if os.path.exists(TEMP_CONFIG_FILE_WITH_TIMESTAMP):
            os.remove(TEMP_CONFIG_FILE_WITH_TIMESTAMP)


if __name__ == "__main__":
    main()