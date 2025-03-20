#!/usr/bin/python3
#
# Copyright (c) 2022 Cisco and/or its affiliates.
# 
# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.1 (the "License"). You may obtain a copy of the
# License at
# 
#                https://developer.cisco.com/docs/licenses
# 
# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

import argparse
from subprocess import getstatusoutput
import sys, os
import time
from kpkg_cmn import *

cpath   = ""
vpath   = ""
bpath   = ""

dbg     = 0
BUNDLE_COUNT = 3

def setDbg(val):
    global dbg
    dbg = val

def kdbg(*arg):
    if (dbg == 1):
        print(arg)

def kerr(*arg):
    print(arg)

def create_main_keys():
    cmd = "openssl req -new -x509 -newkey rsa:2048 -subj \"/CN=OC_KEY/\" -keyout oc-single-priv.key -out oc-single.pem -days 365 -nodes -sha256"
    kdbg("Creating signer keys with cmd: "+cmd)
    status, log = getstatusoutput(cmd)
    kdbg(log)
    if (status != 0) or ("writing new private key" not in log):
        kerr("Failed to create necessary signer keys: "+log)
        quit()

def create_test_key():
    cmd = "openssl req -new -x509 -newkey rsa:2048 -subj \"/CN=OC_KEY/\" -keyout Test-priv.key -out Test.pem -days 365 -nodes -sha256"
    kdbg("Creating test keys with cmd: "+cmd)
    status, log = getstatusoutput(cmd)
    kdbg(log)
    if (status != 0) or ("writing new private key" not in log):
        kerr("Failed to create test keys: "+log)
        quit()
    
def run_kpkg_test(signed):
    if signed:
        val = " "
        op = "./signed.kpkg"
    else:
        val = " -n "
        op = "./unsigned.kpkg"
    
    cmd = cpath+val+"  -o ADD -t ALLOWED_LIST -u CUS-CT -a \"key:value,\" -i ./Test.pem -p ./oc-single.pem -r ./oc-single-priv.key -f "+op
    kdbg("Creating key package with command: \n"+cmd)
    status, log = getstatusoutput(cmd)
    kdbg(log)
    if (status != 0) or ("package generated" not in log):
        kerr("Failed to create key package: "+log)
        quit()
    cmd = vpath+val+"  -p ./oc-single.pem -f "+op
    kdbg("Verifying key package with command: \n"+cmd)
    status, log = getstatusoutput(cmd)
    kdbg(log)
    if (status != 0) or ("Key package is valid" not in log):
        kerr("Failed to verify key package: "+log)
        quit()
    if signed:
        print("Signed key package test SUCCESS.")
    else:
        print("Unsigned key package test SUCCESS.")

def create_bundle_source_keys(tgt_list):
    for x in range(0, BUNDLE_COUNT):
        skey_name = "Test_Key_"+tgt_list+"_"+str(x)+".pem"
        cmd = "openssl req -new -x509 -newkey rsa:2048 -subj \"/CN=OC_KEY/\" -keyout Test-priv.key -out "+skey_name+" -days 365 -nodes -sha256"
        kdbg("Creating TEST key with cmd: "+cmd)
        status, log = getstatusoutput(cmd)
        kdbg(log)
        if (status != 0) or ("writing new private key" not in log):
            kerr("Failed to create test keys: "+log)
            quit()

def generate_keypackages(tgt_list, signed):
    if signed:
        val = " "
    else:
        val = " -n "

    if tgt_list == trgt[0]:
        usg = "U_A_"
    else:
        usg = "U_R_"

    for x in range(0, BUNDLE_COUNT):
        usage = usg+str(x)
        key_name = "key_"+tgt_list+"_"+str(x)+".kpkg"
        skey_name = "Test_Key_"+tgt_list+"_"+str(x)+".pem"
        cmd = cpath+val+"  -o ADD -t "+tgt_list+" -u "+usage+" -a \"key:value,\" -i "+skey_name+" -p ./oc-single.pem -r ./oc-single-priv.key -f "+key_name
        kdbg("Creating key package with command: \n"+cmd)
        status, log = getstatusoutput(cmd)
        kdbg(log)
        if (status != 0) or ("package generated" not in log):
            kerr("Failed to create key package: "+log)
            quit()
        time.sleep(1)

def generate_bundle(signed):
    if signed:
        sarg = " "
        op = "signed.bundle.kpkg"
    else:
        sarg = " -n "
        op = "un_signed.bundle.kpkg"

    blist = " "
    for x in range(0, BUNDLE_COUNT):
        key_name = " key_ALLOWED_LIST_"+str(x)+".kpkg"
        blist += key_name
    for x in range(0, BUNDLE_COUNT):
        key_name = " key_REVOKED_LIST_"+str(x)+".kpkg"
        blist += key_name
    cmd = bpath+" -p ./oc-single.pem -r ./oc-single-priv.key "+sarg+" -f "+op+" -l "+blist
    kdbg("Creating key package Bundle with command: \n"+cmd)
    status, log = getstatusoutput(cmd)
    kdbg(log)
    if (status != 0) or ("Failed" in log):
        kerr("Failed to create key package: "+log)
        quit()

def verify_bundle(signed):
    if signed:
        sarg = " "
        op = "signed.bundle.kpkg"
    else:
        sarg = " -n "
        op = "un_signed.bundle.kpkg"

    cmd = vpath+sarg+"  -p ./oc-single.pem -f "+op
    kdbg("Verifying key package with command: \n"+cmd)
    status, log = getstatusoutput(cmd)
    kdbg(log)
    if (status != 0) or ("Key package is valid" not in log):
        kerr("Failed to verify key package: "+log)
        quit()
    if signed:
        print("Signed key package BUNDLE test SUCCESS ")
    else:
        print("Unsigned key package BUNDLE test SUCCESS.")
    
def run_bundle_test(signed):
    create_bundle_source_keys(trgt[0])
    create_bundle_source_keys(trgt[1])

    if signed:
        generate_keypackages(trgt[0], SIGNED)
        generate_keypackages(trgt[1], SIGNED)
        generate_bundle(SIGNED)
        verify_bundle(SIGNED)
    else:
        generate_keypackages(trgt[0], UNSIGNED)
        generate_keypackages(trgt[1], UNSIGNED)
        generate_bundle(UNSIGNED)
        verify_bundle(UNSIGNED)

def main():
    parser = argparse.ArgumentParser(description="Test keypackage scripts")
    parser.add_argument('-k', '--nocreate', required=False, action='store_true',
                        help="Don't create keys, just test with existing keys.")
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help="Verbose information")
    args = parser.parse_args()

    if args.verbose:
        setDbg(1)

    global cpath
    global vpath
    global bpath

    cpath = os.path.dirname(sys.argv[0])+"/create_kpkg.py"
    vpath = os.path.dirname(sys.argv[0])+"/verify_kpkg.py"
    bpath = os.path.dirname(sys.argv[0])+"/bundle_kpkg.py"
    
    kdbg("Cpath: "+cpath)
    kdbg("Vpath: "+vpath)
    kdbg("Bpath: "+bpath)

    if not args.nocreate:
        # Create necessary keys.
        create_main_keys()
    else:
        kdbg("SKIP creating keys.")

    create_test_key()

    print("Running single key package tests...")

    # Run Un-signed keypackage test
    run_kpkg_test(UNSIGNED)

    # Run signed keypackage test
    run_kpkg_test(SIGNED)

    print("Running key package bundle tests...")

    # Run Unsigned Bundle
    run_bundle_test(UNSIGNED)

    # Run Signed Bundle
    run_bundle_test(SIGNED)

if __name__ == "__main__":
    main()
