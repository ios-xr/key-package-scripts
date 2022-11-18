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
from kpkg_cfg import *

def main():

    parser = argparse.ArgumentParser(description="Generate a Key Signed Package.  "
                            "Or Generate an unsigned key package. ")
    parser.add_argument('-o', '--operation', required=True, choices=oper,
                        help="Key Package Operation")
    parser.add_argument('-t', '--target', required=True, choices=trgt,
                        help="Target/destination of Operation")
    parser.add_argument('-u', '--usage', required=True, type=str,
                        help="Usage for which this key package is being generated")
    parser.add_argument('-a', '--additional', required=False, type=str,
                        help="Additional key related information")
    parser.add_argument('-d', '--timestamp', required=False, type=str,
                        help="In RFC 2822 format, time at which this key package is being generated")
    parser.add_argument('-k', '--keytype', required=False, choices=ktyp,
                        help="Type of key")
    parser.add_argument('-n', '--nosign', required=False, action='store_true',
                        help="Generate key package but don't sign.")
    parser.add_argument('-x', '--tempdir', required=False, help="Temporary directory to be used")
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help="Verbose information")
    parser.add_argument('-i', '--input', required=True, type=str,
                        help="Public Key to be packaged in Key-Package")
    parser.add_argument('-p', '--pubkey', required=False, help="Signer public key")
    parser.add_argument('-r', '--privkey', required=False, help="Signer private key")
    parser.add_argument('-f', '--keypackage', required=True, type=str,
                        help="Generated/output key package")

    args = parser.parse_args()

    # Set debug
    if args.verbose:
        setDbg(1)

    # Rule 1 : Revoked List Keys cannot be deleted (can be enforced in tool)
    # Rule 2 : Revoked List Key cannot be overwritten (cannot be enforced
    #               in tool, but enforced in code).
    if args.operation == "DELETE" and args.target == "REVOKED_LIST":
        print("Deleting keys from Revoked List is not allowed.")
        print("On router use \"clear device ownership challenge/response\" " )
        print(" cli to zeroize keys")
        quit()

    # CLI check 1
    if args.usage == "CUSTOMER-CONSENT-TOKEN" or args.usage == "CUS-CT":
        if not args.additional:
            print("USAGE CUSTOMER-CONSENT-TOKEN/CUS-CT is reserved for customer consent-token keys \n" + 
                  "For Customer Consent-token keys, \"--additional\" field is mandatory")
            quit()
        # Setting internal name for Customer consent-token keys    
        args.usage = "CUS-CT"    


    # Set temporary directory
    setTemp(args.tempdir)

    # Create config file
    cfg = KConfig()
    cfg.SetParam(args.operation, args.target, args.usage, args.additional, args.timestamp, args.keytype)
    cfg.GenerateConfig()

    # Generate TAR file
    makeTar(cfg.GetFileName(), args.input)

    if args.nosign:
        # Generate Unsigned key package
        unsignedTar(args.keypackage)
        print("Unsigned key package generated at:"+args.keypackage)
        kcleanup_exit()

    # Generate Signed key package
    # make sure keys are provided
    if not args.pubkey or not args.privkey:
        print("Public key and private key are needed for signing keypackage")
        print("Options -p or -r empty")
        kcleanup_exit()

    #Sign TAR file
    signTar(args.pubkey, args.privkey, args.keypackage)

    # All done
    print("Key package generated at: "+args.keypackage)
    kcleanup_exit()

if __name__ == "__main__":
    main()

