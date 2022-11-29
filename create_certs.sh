#!/bin/bash -xe
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

# Sample script to generate sample certs for device ownership establishment

if [ "$1" == "-r" ]; then
    rm *.key *.pem *.der *.csr *.srl *.h *.cms MyOpenssl.conf 2>/dev/null
    exit 0
fi

cat << __EOF__ >MyOpenssl.conf

[ req ]
distinguished_name       = distinguished_name
extensions               = int_ca
req_extensions           = int_ca

[ int_ca ]
basicConstraints         = CA:TRUE

[ distinguished_name ]
__EOF__

#create PDC (Root CA)
openssl genrsa -out pdc-priv.key 2048
openssl req -new -x509 -days 1826 -key pdc-priv.key -out pdc.pem -subj "/C=US/O=xzy/OU=abc/CN=ROOT-CN"

#create Intermediate CA
openssl genrsa -out intermediate-ca-priv.key 2048
openssl req -new -sha256 -key intermediate-ca-priv.key -nodes -out intermediate-ca.csr -subj "/C=US/O=xyz/OU=abc/CN=INTERIM-CN"
openssl x509 -req -days 1000 -extfile MyOpenssl.conf -extensions int_ca -in intermediate-ca.csr -CA pdc.pem -CAkey pdc-priv.key -CAcreateserial -out intermediate-ca.pem

#create OC
openssl genrsa -out oc-chain-priv.key 2048
openssl req -new -key oc-chain-priv.key -out oc-chain.csr -subj "/C=US/O=xyz/OU=abc/CN=USER-CN"
openssl x509 -req -in oc-chain.csr -CA intermediate-ca.pem -CAkey intermediate-ca-priv.key -set_serial 01 -out oc-chain.pem -days 500 -sha1

#convert pem to der
openssl x509 -outform der -in pdc.pem -out pdc.der
xxd --include pdc.der >pdc.h
openssl x509 -outform der -in intermediate-ca.pem -out intermediate-ca.der
openssl x509 -outform der -in oc-chain.pem -out oc-chain.der

#use intermediate ca cert also as one level OC
cp intermediate-ca.pem oc-single.pem
cp intermediate-ca.der oc-single.der
cp intermediate-ca-priv.key oc-single-priv.key

#create customer CT cert
openssl genrsa -out cust-ct-priv.key 2048
openssl req -new -sha256 -key cust-ct-priv.key -nodes -out cust-ct.csr -subj "/C=US/O=xyz/OU=abc/CN=CUST-CT-CN"
openssl x509 -req -days 1000 -in cust-ct.csr -CA pdc.pem -CAkey pdc-priv.key -set_serial 02 -out cust-ct.pem
openssl x509 -outform der -in cust-ct.pem -out cust-ct.der
xxd --include cust-ct.der >cust-ct.h

#verify cust ct cert with private key
openssl x509 -noout -modulus -in cust-ct.pem | openssl md5
openssl rsa -noout -modulus -in cust-ct-priv.key | openssl md5
openssl req -noout -modulus -in cust-ct.csr | openssl md5

#create OC single and chained CMS
openssl crl2pkcs7 -nocrl -certfile intermediate-ca.pem -outform der -out oc-single.cms
openssl crl2pkcs7 -nocrl -certfile pdc.der -certfile intermediate-ca.der -certfile oc-chain.der -outform der -out oc-chain.cms

#verify cert chain
openssl verify -verbose -CAfile pdc.pem intermediate-ca.pem
openssl verify -verbose -CAfile <(cat pdc.pem intermediate-ca.pem) oc-chain.pem
openssl verify -verbose -CAfile pdc.pem -untrusted intermediate-ca.pem oc-chain.pem
openssl verify -verbose -CAfile pdc.pem cust-ct.pem
