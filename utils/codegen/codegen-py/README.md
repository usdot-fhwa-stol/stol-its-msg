## Steps to generate decoding functions

### Prerequisites

- Make sure you place your spec files in asn1/raw/carma_j2735

###

### Steps

- Create a python environment
    - `python3 -m venv venv`
    - `. ./venv/bin/activate` for mac os
    - `venv\Scripts\activate` for windows
    - `pip3 install -r utils/codegen/codegen-py/requirements.txt`

- Run the following script that checks for docker, cmake and installs them if not found, this also copies the parser.py (copies this file to asn1tools - temporary fix)
    - source setup.sh


- To generate .c and .h files for a given specification files
    - `python3 utils/codegen/asn1ToC/asn1ToC.py asn1/raw/carma_j2735/ -o stol_its_coding`


- To generate decoding functions for list of specification files in asn1/raw/carma_j2735 (this generates the conversion functions in stol_its_conversion )
    - `python3 utils/codegen/codegen-py/codeGeneration.py -o stol_its_conversion --log-level DEBUG`

- To build the project 
    - `chmod +x build.sh` (one time command)
    - `./build.sh -DCODING_INPUT_DIR=stol_its_coding -DCONVERSION_INPUT_DIR=stol_its_conversion`

> **Important:** 
Argumets CODING_INPUT_DIR, CONVERSION_INPUT_DIR passed to build.sh should be same as -o arguments from previous steps.