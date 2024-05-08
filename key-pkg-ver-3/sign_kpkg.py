import subprocess, json, os
from utils.create_kpkg_helper import *
from utils.input_utils import *
from validate_kpkg import *

TEMP_CONFIG_FILE_WITH_TIMESTAMP = 'modified_config_with_ts.json'


def add_timestamp(config_file_input_path, timestamp):
    '''Add timestamp, if timestamp value is blank, generate and add.
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
    parser = argparse.ArgumentParser(description = "Validate a manually created key package .json file")
    parser.add_argument('-f', '--keypackage', required = True, help = "Path to Key Package .json config file ")
    parser.add_argument('-p', '--publickey', required = True, help = "Path to Public Key file ")
    parser.add_argument('-r', '--privatekey', required = True, help = "Path to Private Key file ")
    parser.add_argument('-t', '--timestamp', required = False, help = "timestamp (in 'date -R' format) ")
    parser.add_argument('-o', '--output', required = True, help = "Filename for output signed file")


    args = parser.parse_args()



    if not os.path.isfile(args.keypackage):
        print("ERROR: Please enter a valid key package .json config file path to be signed.")
        return

    if not os.path.isfile(args.publickey):
        print("ERROR: Please enter a valid public key file path.")
        return
    if not os.path.isfile(args.privatekey):
        print("ERROR: Please enter a valid private key file path.")
        return

    timestamp = None
    if args.timestamp:
        is_valid_timestamp = validate_timestamp(args.timestamp)
        if isinstance(is_valid_timestamp, bool) and is_valid_timestamp is True:
            timestamp = args.timestamp
        else:
            print('Please input a valid timestamp, closed with ""(in "date -R" format):\n')
            return

    validate_kpkg(args.keypackage)
    try:
        add_timestamp(args.keypackage, timestamp)
    except Exception as e:
        print("Couldn't add timestamp to config file!")
    else:
        sign_kpkg(args.publickey, args.privatekey, TEMP_CONFIG_FILE_WITH_TIMESTAMP, args.output)
    finally:
        if os.path.exists(TEMP_CONFIG_FILE_WITH_TIMESTAMP):
            os.remove(TEMP_CONFIG_FILE_WITH_TIMESTAMP)


if __name__ == "__main__":
    main()