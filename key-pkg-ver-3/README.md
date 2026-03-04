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

```bash
python3 create_kpkg.py -u TESTG -k GPG -i ./test.gpg -f ~/kpkg_testg.json
```

- `-u` - Name of the keys (the keys will be stored with this name on the device)
- `-k` - Type of key (only `GPG` and `X509` are supported)
- `-i` - File containing the key content
- `-f` - Output file

The output file will be a json file bundling the given details. This file can also be created manually if needed.

### Step-2: Validate Key Packages (if created manually)

```bash
python3 validate_kpkg.py -f kpkg_testg.json
```

- `-f` - The key package config (`.json`) file to validate.

The script will check the given .json file for its validity. This validation script is useful when you want to create the key package configuration file manually, instead of using create_kpkg.py to create it.

### Step-3: Sign Key Packages

```bash
python3 sign_kpkg.py \
  -A kpkg_key1.json,kpkg_key2.json \
  -R kpkg_key3.json \
  -p pub_key.pem \
  -r priv.key \
  -o out.kpkg \
  -t "Mon, 03 Feb 2024 17:14:35 +0530"
```

Arguments:

- `-A` - Allowed list: comma-separated per-key JSON files (no spaces).
- `-R` - Revoked list: comma-separated per-key JSON files (no spaces).
- `-p` - Ownership cert file.
- `-r` - Ownership private key file.
- `-o` - Output file name (created by the script).
- `-t` - (Optional) Timestamp (must match `date -R` output). If omitted, the current system timestamp is used.
- `-n` - (Optional) Generate combined JSON but do not sign.

Notes:

- The script combines keys provided via `-A` into `ALLOWED_LIST` and keys provided via `-R` into `REVOKED_LIST`.
- If either `-A` or `-R` is not provided, that list is omitted from the generated payload.
- If an empty file is provided after either `-A` or `-R`, that list becomes empty (`[]`) in the generated payload.
