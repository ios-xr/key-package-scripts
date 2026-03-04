import sys, argparse
from utils.input_utils import *

def main():
    parser = argparse.ArgumentParser(description = "Validate a key package .json file")
    parser.add_argument('-f', '--keypackage', required=True, help="Path to Key package json file to be validated")
    args = parser.parse_args()

    ret = validate_key_package(args.keypackage)
    if not ret:
        print("Key package validation failed")
        sys.exit(0)

    print("Key package validation successful")

if __name__ == "__main__":
    main()