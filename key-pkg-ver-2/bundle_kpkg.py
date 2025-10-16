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
import json
import shutil
import time
import os
from kpkg_cfg import *

alist = {}
rlist = {}
fin = {"ALLOWED_LIST":[], "REVOKED_LIST":[]}

TEMPDIR   = ""
CONFIG_FILE = "config.txt"

def bcleanup_exit():
    cmd = RMCMD+TEMPDIR
    kdbg("Cleaning up with:"+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        kerr("Failed to cleanup temp directory: "+log)
    quit()

def cleanupTemp():
    cmd = RMCMD+TEMPDIR+"/* "
    kdbg("TEMP cleanup with Cmd: "+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        print("Failed to cleanup TEMP:"+log)
        bcleanup_exit()
    
def createTemp():
    cmd = MKDIRCMD+TEMPDIR
    kdbg("TEMP with Cmd: "+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        print("Failed to Create TEMP:"+log)
        bcleanup_exit()

def verifySinglePkg(pkgf, pubkey):
    ssl_cmd = "openssl smime -inform DER -verify -CAfile "
    ssl_cmd += pubkey+" -partial_chain -in "+pkgf+" -out "+TEMPDIR+TARFILE
    kdbg("Cmd: "+ssl_cmd)
    status, log = getstatusoutput(ssl_cmd)
    if (status != 0) or ("Verification successful" not in log):
        print("Failed to verify file:"+log)
        bcleanup_exit()

def SortList(ilst, tgt):
    op = {}
    for x in ilst:
        ts = ilst[x]
        ts = ts[:-6]
        epoch = int(time.mktime(time.strptime(ts, "%a, %d %b %Y %H:%M:%S")))
        op[x] = epoch
    s = sorted(list(op.items()), key=lambda x: x[1])
    kdbg("Sorted: "+tgt)
    kdbg(s)
    dup_check = []
    for z in range(0, (len(s))):
        if s[z][1] in dup_check:
            print("Error: Duplicate timestamp found in one of the keys")
            bcleanup_exit()
        fin[tgt].append(os.path.basename(s[z][0]))
        dup_check.append(s[z][1])

def keyProcess (kpath, pubkey, privkey, nosign):
    fname = TEMPDIR+os.path.basename(kpath)
    kdbg("Copying: "+kpath+" To Dest: "+TEMPDIR)

    # Copy file
    shutil.copy(kpath, TEMPDIR)

    if not nosign:
        # Verify Key package
        verifySinglePkg(fname, pubkey)
    else:
        shutil.copyfile(fname, TEMPDIR+TARFILE)

    # Untar file
    cmd = UNTAR+TEMPDIR+ " -xvf "+TEMPDIR+TARFILE
    kdbg("Untar cmd: "+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        print("Failed to Untar file:"+log)
        quit()

    # Got JSON config file.
    json_file = TEMPDIR + CONFIG_FILE
    with open(json_file, 'r') as f:
        jobj = json.load(f)
        kdbg(jobj)
        if jobj["TARGET"] == "ALLOWED_LIST":
            alist[fname] = jobj["TIMESTAMP"]
        else:
            rlist[fname] = jobj["TIMESTAMP"]

    # Cleanup for next call.
    cleanupTemp()

def makeBundleTar(flist):
    cmd = TAR+" "+TEMPDIR+TARFILE+" -C "+TEMPDIR+"  "+CONFIG+" "
    for file in flist:
        shutil.copy(file, TEMPDIR)
        cmd += " "+os.path.basename(file)
    kdbg("Creating TAR file with cmd: "+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        print("Failed to create TAR: "+log)
        bcleanup_exit()

def signBundleTar(pubkey, privkey, op):
    cmd = ssl_cmd = "openssl smime -sign -binary "
    cmd = (ssl_cmd+" -in "+TEMPDIR+TARFILE+" -signer "+pubkey+
            " -outform DER -inkey "+privkey+" -nodetach -out "+op)
    kdbg("Signing with cmd:"+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        print("Failed to sign key package: "+log)
        bcleanup_exit()

def main():
    
    parser = argparse.ArgumentParser(description="Generate a Signed Key Package Bundle.  "
                            "Or Generate an unsigned Key Package Bundle. ")
    parser.add_argument('-n', '--nosign', required=False, action='store_true',
                        help="Generate key package bundle but don't sign it.")
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help="Verbose information")
    parser.add_argument('-x', '--tempdir', required=False, help="Temporary directory to be used")
    parser.add_argument('-l', '--list', required=True, nargs='+', 
                        help="List of key packages to be bundled.")
    parser.add_argument('-p', '--pubkey', required=True, help="Bundle signer public key")
    parser.add_argument('-r', '--privkey', required=True, help="Bundle signer private key")
    parser.add_argument('-f', '--keypackage', required=True, type=str,
                        help="Generated/output key package bundle")

    args = parser.parse_args()

    # Set debug
    if args.verbose:
        setDbg(1)

    # TEMP dir
    global TEMPDIR
    if args.tempdir:
        TEMPDIR = args.tempdir+"/"
    else:
        TEMPDIR = "/tmp/KPKG_TMPDIR/"
    createTemp()
    cleanupTemp()

    # Go thru the list of input key packages
    #   and sort them based on target and timestamp
    for kpkg in args.list:
        keyProcess(kpkg, args.pubkey, args.privkey, args.nosign)

    # Now sort All ALLOWED LIST keys
    SortList(alist, "ALLOWED_LIST")

    # Sort All REVOKED LIST keys
    SortList(rlist, "REVOKED_LIST")
    
    # Dump the final list of sorted keys
    kdbg("Final List of sorted keys: ")
    kdbg(fin)

    # Generate config file

    # Content for config file
    config_file = {}

    # Add version information
    # This will be version 2
    config_file[json_key_str[0]] = 2
    # SET Bundle flag to TRUE
    config_file[json_key_str[7]] = 1
    # Set KEY List
    config_file[json_key_str[8]] = fin
    jobj = json.dumps(config_file, indent = 4)
    
    # Dump config content to file
    cfile = TEMPDIR+CONFIG
    f = open(cfile, "w")
    f.write(jobj)
    f.close()

    # Generate TAR file
    makeBundleTar(args.list)

    if args.nosign:
        # Generate Unsigned key package bundle
        shutil.copyfile(TEMPDIR+TARFILE, args.keypackage)
        print("Unsigned key package generated at:"+args.keypackage)
        bcleanup_exit()

    # Generate Signed key package bundle
    # make sure keys are provided
    if not args.pubkey or not args.privkey:
        print("Public key and private key are needed for signing keypackage")
        print("Options -p or -r empty")
        bcleanup_exit()

    #Sign TAR file
    signBundleTar(args.pubkey, args.privkey, args.keypackage)

    # All done
    print("Key package Bundle generated at: "+args.keypackage)
    bcleanup_exit()

if __name__ == "__main__":
    main()

