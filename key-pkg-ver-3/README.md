# Key Package Generation, validation and signing

These scripts have been validated only with python 3.6.7

## Introduction

In key-pkg-ver-3, only the UPDATE operation is supported. When UPDATE operation is done, the set of existing keys is deleted and the new set of keys part of the UPDATE key-pkg is installed. Effectively, its a complete replacement of the key package contents.

The steps to follow are:

1. Create key packages config file (.json) by running create_kpkg.py file or prepare it manually.
2. Validate config file (.json), if ***created manually***, by running validate_kpkg.py.
3. Sign key package config file (.json) by running sign_kpkg.py to get the final key-package.

Mentioned 3 steps have been described below:

### Step-1: Create Key Packages

create_kpkg.py -u TESTG -k GPGKEY -i ./test.gpg -f ~/kpkg_testg.json

        -u - Name of the keys (The keys will be stored with this name in the device)
        -k - Type of key (Only GPGKEY and X509KEY supported)
        -i - File containing the key content
        -f - Output file

The output file will be a json file bundling the given details. This file can also be created manually if needed.

### Step-2: Validate Key Packages (if created manually)

python3 validate_kpkg.py -f kpkg_testg.json

        - f - The key package config (.json) file which have to be validated.

The script will check the given .json file for its validity. This validation script is useful when you want to create the key package configuration file manually, instead of using create_kpkg.py to create it.

### Step-3: Sign Key Packages

python3 sign_kpkg.py -A kpkg_key1.json, kpkg_key1.json -R kpkg_key3.json -p pub_key.pem -r priv.key -o out.kpkg -t "Mon, 03 Feb 2024 17:14:35 +0530"

The following required argument should be provided:-

- A - For Allowed list. The json files of each key can be given comma separated
- R - For Revoked list. The json files of each key can be given comma separated
- p - Ownership cert file.
- r - Ownership private key file.
- o - Output file name (File with this name will be created by script).
- t - (Optional) Timestamp (in "date -R" output format), if not provided, it will
      take the current system's timestamp.

The script will add the json key files provided after the -A argument to the allowed list and after -R argument to the revoked list. If either -A or -R is not provided, that target will be untouched on the device. If an empty key file is provided after either the -A or -R argument, this will clear that target.
