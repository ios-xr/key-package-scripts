This page summarizes the process of creation of Key Package

        - key-pkg-ver-1 should be used for XR releases 76x and 77x
        - key-pkg-ver-2 should be used for XR releases 78x and above

## Why is Key Package needed.

The end goal of Key Package infrastructure is to provide user a secure mechanism to install Customer signed software or a secure way for customer to send Customer Signed Consent Requests. Key-package is a conduit used to securely onboard public/verification keys of 3rd party non-cisco customers, onto XR devices.


## What is Key Package

Key package is a CMS file (Cryptographic Message Syntax - RFC5652) which is digitally signed by the Ownership Certificate (OC), and having a payload. The payload is a tar of the customer/3rd party keys which are to be onboarded onto the system, along with a configuration file config.txt which contains details on what actions to be performed with the key.

## Pre-requisites - Establish Device Ownership

A customer has to establish device ownership, as part of which the Ownership Certificate (OC) will be installed into hardware secure storage (TAM) of the customer’s router. Without device ownership established, one cannot install 3rd party key packages onto the system. 

Confirm device ownership is established by issuing command: "show platform security device-ownership"


---


