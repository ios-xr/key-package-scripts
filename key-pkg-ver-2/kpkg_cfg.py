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

import json
from kpkg_cmn import *

TARFILE = "a.tar"

def setTemp(val):
    global tmp
    global tar_fname
    if not val:
        tmp = TEMPDIR
    else:
        tmp = val+"/KPKG_TMPDIR/"
    tar_fname = tmp + TARFILE
    # Delete TEMP directory to start with
    kdbg("Creating TEMP directory: "+tmp)
    status, log = getstatusoutput(RMCMD+tmp)
    if (status != 0):
        print("Failed to cleanup temp directory: "+log)
        kcleanup_exit()
    # Create TEMP directory
    status, log = getstatusoutput(MKDIRCMD+tmp)
    if (status != 0):
        print("Failed to create temp directory: "+log)
        kcleanup_exit()

def makeTar(f1, f2):
    global tmp
    global tar_fname
    cmd = "cp "+f2+" "+tmp+" ;"
    head, key = os.path.split(f2)
    cmd += TAR+" "+tar_fname+" -C "+tmp+" "+f1+" "+key
    kdbg("Creating TAR file with cmd: "+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        print("Failed to create TAR: "+log)
        kcleanup_exit()

def signTar(pubkey, privkey, op):
    global tmp
    global tar_fname
    ssl_cmd = "openssl smime -sign -binary "
    cmd = (ssl_cmd+" -in "+tar_fname+" -signer "+pubkey+
            " -outform DER -inkey "+privkey+" -nodetach -out "+op)
    kdbg("Signing with cmd:"+cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        print("Failed to sign key package: "+log)
        kcleanup_exit()

def unsignedTar(op):
    global tar_fname
    cmd = "cp "+tar_fname+" "+op
    kdbg("Copying unsigned tar with cmd: ", cmd)
    status, log = getstatusoutput(cmd)
    if (status != 0):
        print("Failed to copy unsigned key package: "+log)
        kcleanup_exit()

class KConfig:

#
# VERSION
# For internal use. Leave it as is.
#
    VERSION_VAL = 2

#
# Key Package OPERATION
#
# Mandatory String.
#
# Use this flag to indicate whether the keys to be created or
# deleted from the system.
#
# Allowed Values:
# ADD - New keys are to be created/written
# DELETE - Delete existing keys
#
    operation_val = ""


#
# Key Package TARGET
#
# Mandatory String
#
# Use this flag to indicate in which list the keys should be inserted.
#
# Allowed Values:
# ALLOWED_LIST - Allowed List Keys
# REVOKED_LIST - Revoked List Keys
#
    target_val = ""

#
# Key Package USAGE
#
# Mandatory String
# Use this flag to indicate the usage for which this key package is being installed
#
# Allowed Values:
# 6 character user defined string without special characters, eg
# USAGE = CU_XYZ
#
    usage_val = ""

#
# Key package optional information
#
# Optional String
# Use this flag to pass any optional information regarding keys
# to the infra.
#
# Allowed Values:
# key1:Value1,key2:Value2,key3:Value3,
#
    addtional_val = ""

#
# The time at which this key package was
# generated. Timestamp should be in RFC 2822 format.
#
# Linux command "date -R" generates current timestamp
# in RFC 2822 format.
#
# NOTE: Valid YEAR of timestamp should be
#       between 2000 and 2100
#
# Eg: Wed, 18 Jun 2001 16:14:19 +0530
#
#
    timestamp_val = ""

#
# KEYTYPE
# Indicates what this key type is.
#
# This is Optional string.
#
# Allowed Values:
# X509KEY - Key being onboarded is an X509 Cert
# GPGKEY - Key being onboarded is a GPG key
#
    keytype_val = ""

#
# End of config
#

    def __init__(self):
        global CONFIG
        self.name = CONFIG

    def __getts__(self):
        cmd = "date -R"
        status, log = getstatusoutput(cmd)
        if (status != 0):
            kerr("Failed to run command: "+cmd)
            kcleanup_exit()
        return(log)

    def __writetofile__(self, fname, buf):
        global tmp
        c = tmp+fname
        try:
            with open(c, "w") as f:
                #kdbg("Writing to file: "+buf)
                f.write(buf)
        except:
            print("Error: Failed to write file to disk.")
            kcleanup_exit()
        kdbg("Created file: "+c)

    def GetFileName(self):
        return(self.name)

    def SetVer(self, ver):
        self.VERSION = ver

    def SetParam(self, op, tgt, usg, additional, ts, kt):

        global USAGE_LEN
        global TIMESTAMP_LEN
        global ADDITIONAL_SZ
        global ADDITIONAL_KEY_LEN
        global ADDITIONAL_DATA_LEN

        self.operation_val = op
        self.target_val = tgt

        # Check length of USAGE
        sanitizeUsage(usg)
        self.usage_val = usg

        # Has user passed ADDITIONAL arg
        if not additional:
            kdbg("Additional key argument not set")
            self.additional_val = None
        else:
            self.additional_val = additional
            sanitizeAdditional(self.additional_val)
            # Additional checks for CUS-CT USAGE
            if usg == CUSCT:
                # Format is
                # key1:Value1,key2:Value2,key3:Value3
                sanitize_CUS_CT_additional(self.additional_val)

        # User provided Timestamp..?
        if not ts:
            self.timestamp_val = self.__getts__()
            kdbg("Generated timestamp for kpkg:"+self.timestamp_val)
        else:
            self.timestamp_val = ts
            kdbg("User provided TS: "+ts)
        sanitizeTimestamp(self.timestamp_val)

        # User provided key type..?
        # Default is X509
        if not kt:
            self.keytype_val = "X509KEY"
            kdbg("Default key type "+self.keytype_val)
        else:
            self.keytype_val = kt
            kdbg("User provided key type: "+kt)

    def GenerateConfig(self):
        kdbg("Generating Config file")

        jcfg = {}

        # Dump VERSION info.
        jcfg[json_key_str[0]] = self.VERSION_VAL

        # Dump Operation
        jcfg[json_key_str[1]] = self.operation_val

        # Dump Target
        jcfg[json_key_str[2]] = self.target_val

        # Dump Usage
        jcfg[json_key_str[3]] = self.usage_val

        # Dump Additional flag
        if self.additional_val:
            jcfg[json_key_str[4]] = self.additional_val

        # Dump TIMESTAMP
        jcfg[json_key_str[5]] = self.timestamp_val

        # Dump KEYTYPE
        jcfg[json_key_str[6]] = self.keytype_val

        # Dump everything to file.
        jobj = json.dumps(jcfg, indent = 4)
        self.__writetofile__(self.name, jobj)


