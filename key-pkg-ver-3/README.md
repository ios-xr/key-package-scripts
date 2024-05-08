# Key Package Generation, validation and signing

These scripts have been validated only with python 3.6.7

## Introduction

By using key-pkg-ver-3, you can create ***multiple key packages***, each targeting ***multiple operations***.
We have come up with an interactive key package creation script for better convenience.
Execute the script, it will ask for required information, depending upon your inputs.
The complete process can be divided into 3 simple steps, as follows:

1. Create key packages config file (.json) by running create_kpkg.py file or prepare it manually.
2. Validate config file (.json), if ***created manually***, by running validate_kpkg.py.
3. Sign key package config file (.json) by running sign_kpkg.py.

Mentioned 3 steps have been described below:

### Step-1: Create Key Packages

Run following command:
        python3 create_kpkg.py

- It will ask for to select target list, enter your choice. Depending on your target list selection, it will perform upcoming operations (APPEND, DELETE or REPLACE) on the selected list (1. ALLOWED_LIST, 2. REVOKED_LIST, enter 1 or 2).
- After target list selection, it will ask for to select operation, e.g., 1. APPEND, 2. DELETE or 3. REPLACE. APPEND will add a new key to target list, DELETE will delete a key and REPLACE will replace all the keys.
- After selecting operation, it will ask for to select key type, either 1. X509KEY or 2. GPGKEY. Enter 1 or 2 depending upon your requirements.
- Now you can give name to your key, enter name of the key or press enter to skip. Providing name is optional.
- Now you can input key metadata, which is optional. If you want to add it, type your metadata and press enter, or if you don't want to add it, press enter.
- Now, it will ask for key file path. Give filename of the key where key is stored.
- Further, it will ask for if you want to add more keys to the same key package, if yes, it will allow you to add more keys to this key package, otherwise, you can create new key packages and add keys to that new key package.

### Step-2: Validate Key Packages

Run following command:
        python3 validate_kpkg.py -f kpkg_config.json

- It will check your .json file for its validity.
- This validation script is useful when you want to create the key package
  configuration file manually, instead of using create_kpkg.py to create it.

The following required argument should be provided:-

- f - The key package config (.json) file which have to be validated.

### Step-3: Sign Key Packages

Run following command:
        python3 sign_kpkg.py -f kpkg_config.json -p pub_key.pem -r priv.key -o out.del -t "Mon, 03 Feb 2024 17:14:35 +0530"

The following required argument should be provided:-

- f - The key package config (.json) file.
- p - Public key file.
- r - Private key file.
- o - Output file name (File with this name will be created by script).
- t - (Optional) Timestamp (in "date -R" output format), if not provided, it will
      take the current system's timestamp.

### Additional Information

- You can skip Step-1 and directly start from step-2, by creating your own .json key package file to input in step-2 and step-3.
- You can have multiple operations, e.g., APPEND, DELETE or UPDATE, in one key package. (Note: APPEND is equivalent to ADD, UPDATE is equivalent to REPLACE).
