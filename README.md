This page summarizes the process of creation of Key Package


## Why is Key Package needed.

The end goal of Key Package infrastructure is to provide user a secure mechanism to install Customer signed software or a secure way for customer to send Customer Signed Consent Requests. Key-package is a conduit used to securely onboard public/verification keys of 3rd party non-cisco customers, onto XR devices.


## What is Key Package

Key package is a CMS file (Cryptographic Message Syntax - RFC5652) which is digitally signed by the Ownership Certificate (OC), and having a payload. The payload is a tar of the customer/3rd party keys which are to be onboarded onto the system, along with a configuration file config.txt which contains details on what actions to be performed with the key.

## Pre-requisites - Establish Device Ownership

A customer has to establish device ownership, as part of which the Ownership Certificate (OC) will be installed into hardware secure storage (TAM) of the customer’s router. Without device ownership established, one cannot install 3rd party key packages onto the system. 

Confirm device ownership is established by issuing command: "show platform security device-ownership"

-----------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------

## Creating Key Package

### To Add a GPG Key:
create_kpkg.py -o ADD -t ALLOWED_LIST -u TESTG -k GPGKEY -i ./test.gpg -p ./oc-single.pem -r ./oc-single-priv.key -f ~/test.add
Key package generated at: ~/test.add

### To remove a Key:
create_kpkg.py -o DELETE -t ALLOWED_LIST -u TESTG -k GPGKEY -i ./test.gpg -p ./oc-single.pem -r ./oc-single-priv.key -f ~/test.del
Key package generated at: ~/test.del

### Creating Key Package Bundle
Lets say ~/test1.add and ~/test2.add needs to be bundled into a new key package.

bundle_kpkg.py -l ~/test1.add ~/test2.add -p ./oc-single.pem -r ./oc-single-priv.key -f ~/bundle.key
Key package Bundle generated at: ~/bundle.key

### Verifying Key Package - Tools
verify_kpkg.py -p ./oc-single.pem -f  ~/test.del

The various argument's description is as below:
o - Type of operation (ADD/DELETE)
t - List to operate on (ALLOWED_LIST/REVOKED_LIST)
u - Name of key (key will be stored with this name in XR router)
k - Key type (X509/GPG)
i - Key to be added
p - Signing public key
r - Signing private key
f - Output file 


-----------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------

## Key Package in XR

Once the key-package is created following the above stepse, it can be applied on an IOS-XR box. When the key-package gets successfully 
applied, the keys part of the key-package gets stored securely in the IOS-XR box

### Installation 

platform security key-package customer disk0:/test.add

### Show commands

show platform security key-package customer allowed-list location NAME

show platform security key-package customer revoked-list location NAME
