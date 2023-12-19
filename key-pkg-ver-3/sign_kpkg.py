from utils.create_kpkg_helper import *
import pyinputplus as pyip
import subprocess, json, os, time

TEMP_CONFIG_FILE_WITH_TIMESTAMP = 'modified_config_with_ts.json'

def add_timestamp(config_file_input_path):
    with open(config_file_input_path, 'r') as new_config_file:

        # read
        config_file_data = json.load(new_config_file)
        # get current timestamp
        current_timestamp = None
        cmd_result = subprocess.run(["date", "-R"], stdout=subprocess.PIPE)
        if cmd_result.returncode != 0:
                print("Failed to get timestamp from system")
                print("Singing failed!")
        else:
            current_timestamp = (cmd_result.stdout.decode("utf-8")).strip()
        # add current timestamp
        config_file_data["timestamp"] = current_timestamp


        new_config_file_data = json.dumps(config_file_data, indent=4)

    # open
    with open(TEMP_CONFIG_FILE_WITH_TIMESTAMP, 'w') as new_config_file:

        # write
        print("new_config_file_data#######", new_config_file_data)
        new_config_file.write(new_config_file_data)


def sign_kpkg(public_key_file_path, private_key_file_path, config_input_path, output_path):
    cmd_result = subprocess.run(["openssl", "smime", "-sign", "-binary", "-in", config_input_path, "-signer", public_key_file_path, "-outform", "DER", "-inkey", private_key_file_path, "-nodetach", "-out",  output_path], stdout=subprocess.PIPE)
    if cmd_result.returncode != 0:
        # print("ERROR:\n",cmd_result.stdout.decode("utf-8"))
        print("Singing failed!")
    else:
        print("Singed Successfully!")


def main():
    public_key_file_path = pyip.inputStr(prompt = "Please input public key file path:\n")

    private_key_file_path = pyip.inputStr(prompt = "Please input private key file path:\n")

    kpkg_config_file_input_path = pyip.inputStr(prompt = "Please input key package config file path to be signed :\n")

    

    output_path = pyip.inputStr(prompt = "Please input filename for output:\n")
    try:
        add_timestamp(kpkg_config_file_input_path)
    except:
        print("Couldn't add timestamp to config file!")
    else:
        sign_kpkg(public_key_file_path, private_key_file_path, TEMP_CONFIG_FILE_WITH_TIMESTAMP, output_path)
    finally:
        if os.path.exists(TEMP_CONFIG_FILE_WITH_TIMESTAMP):
            os.remove(TEMP_CONFIG_FILE_WITH_TIMESTAMP)




if __name__ == "__main__":
    main()