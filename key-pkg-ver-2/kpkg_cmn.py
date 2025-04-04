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

import os
import re
from subprocess import getstatusoutput 
from datetime import datetime

TEMPDIR   = "/tmp/KPKG_TMPDIR/"
tmp       = ""
tar_fname = ""
RMCMD     = "rm -rf "
MKDIRCMD  = "mkdir -p "
TAR       = "tar -cvf "
UNTAR     = "tar -C "
CONFIG    = "config.txt"
TARFILE     = "a.tar"

CUSCT     = "CUS-CT"

oper = [
    "ADD",
    "DELETE",
]

trgt = [
    "ALLOWED_LIST",
    "REVOKED_LIST",
]

ktyp = [
    "X509KEY",
    "GPGKEY",
]

# Json key Strings
json_key_str = [
    "VERSION",             #0
    "OPERATION",           #1
    "TARGET",              #2
    "USAGE",               #3
    "USAGE_ADDITIONAL_DATA",   #4
    "TIMESTAMP",           #5
    "KEYTYPE",             #6
    "MULTIPLE_KEYPACKAGE", #7
    "PACKAGE_LIST",        #8
]

# Buffer Limits
ADDITIONAL_SZ           = 128
ADDITIONAL_KEY_LEN      = 6
ADDITIONAL_DATA_LEN     = 64

USAGE_LEN               = 6
TIMESTAMP_LEN           = 41

dbg       = 0

SIGNED = 1
UNSIGNED = 0

def setDbg(val):
    global dbg
    dbg = val

def kdbg(*arg):
    if (dbg == 1):
        print(arg)

def kerr(*arg):
    print(arg)

def kcleanup():
    cmd = RMCMD+tmp
    kdbg("Cleaning up with:"+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        kerr("Failed to cleanup temp directory: "+log)

def kcleanup_exit():
    kcleanup()
    quit()

def sanitizeOperation(ostr):
    if ostr not in oper:
        print("Invalid Operation String:"+ str(ostr))
        kcleanup_exit()
    kdbg("Operation: "+ostr)

def sanitizeTarget(t):
    if t not in trgt:
        print("Invalid Target String:"+ str(t))
        kcleanup_exit()
    kdbg("Target is: "+t)


def sanitizeUsage(usg):
    if len(usg) > USAGE_LEN:
        print("Error: Maximum length of USAGE is "+str(USAGE_LEN)+" char")
        kcleanup_exit()
    if re.search(r'[^A-Za-z0-9_-]', usg):
        print("Only - , _ and alphanumeric char allowed in USAGE")
        kcleanup_exit()
    kdbg("Usage is :"+usg)
    # All good


def sanitizeAdditional(additional):
    if len(additional) > ADDITIONAL_SZ:
        print("Error: maximum length of additional string is 128 char")
        kcleanup_exit()
    if re.search(r'[^A-Za-z0-9:,_-]', additional):
        print("Only '-' , '_' , ':', ',' and alphanumeric char allowed in additional field")
        kcleanup_exit()
    kdbg("Additional Flag: "+additional)


def sanitize_CUS_CT_additional(additional):
    colon_parsed = 0
    comma_parsed = 0
    for element in additional:
        if element == ":":
            if colon_parsed == 1:
                print("Additional string should be of format: key1:value1,key2:value2,")
                kcleanup_exit()
            colon_parsed = 1
        if element == ",":
            comma_parsed = 1
            if colon_parsed == 0:
                print("Additional string should be of format: key1:value1,key2:value2,")
                kcleanup_exit()
        if colon_parsed == 1 and comma_parsed == 1:
            colon_parsed = 0
            comma_parsed = 0
    # Unmatched key value pair:
    if colon_parsed == 1 or comma_parsed == 1:
        print("Additional string should be of format: key1:value1,key2:value2,")
        kcleanup_exit()
    for item in additional[:-1].split(','):
        if len(item.split(':')[0]) > ADDITIONAL_KEY_LEN:
            print("For CUS-CT max limit of additional keyword is 6")
            kcleanup_exit()
        if len(item.split(':')[1]) > ADDITIONAL_DATA_LEN:
            print("For CUS-CT max limit of additional value is 64")
            kcleanup_exit()
        if not item.split(':')[0] or not item.split(':')[1]:
            print("Additional string should be of format: key1:value1,key2:value2,")
            kcleanup_exit()
        kdbg("Keyword Value is :"+item.split(':')[0]+" AND "+item.split(':')[1])
    # All good


def sanitizeTimestamp(timestamp_val):
    timeobj = None # Initialize before try block
    try:
        timeobj = datetime.strptime(timestamp_val[0:(len(timestamp_val) - 5)],
                                    "%a, %d %b %Y %H:%M:%S ")
    except ValueError as v:
        print("Invalid timestamp provided. Timestamp should be output of \"date -R\"")
        print ("Check RFC 2822 for timestamp format")
        kcleanup_exit()
    if (timeobj.year < 2000) or (timeobj.year > 2100):
        print("Invalid YEAR in timestamp. Should be between 2000 and 2100")
        kcleanup_exit()
    if len(timestamp_val) > TIMESTAMP_LEN:
        print("Length of provided timestamp exceeds limit of 41 char.")
        return 1
    # All good.

def sanitizeKeyType(kt):
    if kt not in ktyp:
        print("Invalid Key type:"+ str(kt))
        kcleanup_exit()
    kdbg("Key Type: "+kt)

