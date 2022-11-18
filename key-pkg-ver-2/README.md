This should be used for XR versions 78x and above
These scripts have been validated only with python2

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
- o - Type of operation (ADD/DELETE)
- t - List to operate on (ALLOWED_LIST/REVOKED_LIST)
- u - Name of key (key will be stored with this name in XR router)
- k - Key type (X509/GPG)
- i - Key to be added
- p - Signing public key
- r - Signing private key
- f - Output file 

---

## Key Package in XR

Once the key-package is created following the above stepse, it can be applied on an IOS-XR box. When the key-package gets successfully 
applied, the keys part of the key-package gets stored securely in the IOS-XR box

### Installation 

platform security key-package customer disk0:/test.add

### Show commands

show platform security key-package customer allowed-list location NAME

show platform security key-package customer revoked-list location NAME
