#!/usr/bin/python
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
from kpkg_cmn import *

TARFILE     = "a.tar"

def unTar():
    cmd = UNTAR+tmp+" -xvf "+tmp+TARFILE
    kdbg("Cmd: "+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        print("Failed to Untar file:"+log)
        kcleanup_exit()


def cleanTemp():
    global tmp
    tmp = TEMPDIR
    cmd = MKDIRCMD+tmp
    kdbg("Cmd: "+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        print("Failed to create temp directory:"+log)
        kcleanup_exit()
    cmd = RMCMD+tmp+"*"
    kdbg("Cmd: "+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        print("Failed to cleanup temp directory:"+log)
        kcleanup_exit()
    kdbg("Temp directory set to: "+tmp)

def sanitizeLine(line):
    if ("#" == line[0]) or ("\n" == line[0]) or ("\r" == line[0]):
        return
    line_parsed = 0
    for s in sacret_str:
        if s in line:
            if s == line[0:len(s)]:
                if s == sacret_str[0]:
                    sanitizeVersion(line[len(s):].strip())
                if s == sacret_str[1]:
                    sanitizeOperation(line[len(s):].strip())
                if s == sacret_str[2]:
                    sanitizeTarget(line[len(s):].strip())
                if s == sacret_str[3]:
                    sanitizeUsage(line[len(s):].strip())
                if s == sacret_str[4]:
                    sanitizeAdditional(line[len(s):].strip())
                if s == sacret_str[5]:
                    sanitizeTimestamp(line[len(s):].strip())
                if s == sacret_str[6]:
                    sanitizeKeyType(line[len(s):].strip())
                line_parsed = 1
                break
    if line_parsed == 0:
        print("Invalid line found:"+line)
        kcleanup_exit()


def sanitizeConfigFile():
    global tmp
    global CONFIG
    try:
        f = open(tmp+CONFIG, "r")
        buf = f.readlines()
        f.close()
    except:
        print("Error. Failed to read config")
        kcleanup_exit()
    for line in buf:
        sanitizeLine(line)

def copyPkg(pkgf, ns):
    global tmp
    dest = ""
    if ns:
        dest = TARFILE
    cmd = "cp "+pkgf+" "+tmp+dest
    kdbg("Cmd: "+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        print("Failed to copy file:"+log)
        kcleanup_exit()

def verifyPkg(pkgf, pubkey):
    global tmp
    head, pfile = os.path.split(pkgf)
    ssl_cmd = "openssl smime -inform DER -verify -CAfile "
    ssl_cmd += pubkey+" -partial_chain -in "+tmp+pfile+" -out "+tmp+TARFILE
    kdbg("Cmd: "+ssl_cmd)
    status, log = getstatusoutput(ssl_cmd)
    if (status != 0):
        print("Failed to verify file:"+log)
        kcleanup_exit()

def main():

    parser = argparse.ArgumentParser(description="Verify a Signed or Unsigned Key Package")
    parser.add_argument('-p', '--pubkey', required=False, help="Verification public key")
    parser.add_argument('-f', '--keypackage', required=True, type=str,
                        help="Key package to be verified")
    parser.add_argument('-n', '--nosign', required=False, action='store_true',
                        help="Unsigned Key Package to be verified.")
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help="Verbose information")

    args = parser.parse_args()

    # Set debug
    if args.verbose:
        setDbg(1)

    if not args.nosign:
        if not args.pubkey:
            print("Valid public key is needed for verifying signed packages")
            kcleanup_exit()

    # Set TEMP directory
    cleanTemp()

    # Misc
    copyPkg(args.keypackage, args.nosign)

    if not args.nosign:
        # Verify Key package
        verifyPkg(args.keypackage, args.pubkey)

    # Untar file
    unTar()

    # Sanitize config.txt
    sanitizeConfigFile()

    print("Key package is valid")

if __name__ == "__main__":
    main()

