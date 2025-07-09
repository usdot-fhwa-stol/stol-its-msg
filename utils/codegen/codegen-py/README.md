## Steps to generate decoding functions

### Prerequisites

- Make sure docker daemon is up and running
    - `sudo systemctl start docker` (for ubuntu)
    - use docker desktop for mac os (for mac os and windows)
- Make sure TestMessage01.asn is present in asn1/raw/carma_j2735

###

### Steps

- Create a python environment
    - `python3 -m venv venv`
    - `. ./venv/bin/activate` for mac os
    - `venv\Scripts\activate` for windows
    - `pip3 install -r utils/codegen/codegen-py/requirements.txt`

- To generate .c and .h files for a given specification file (current command is for TestMessage01.asn replace the file path with any desirable file)
    - `python3 utils/codegen/asn1ToC/asn1ToC.py asn1/raw/carma_j2735/TestMessage01.asn -t carma_j2735 -o stol_its_coding`

- To generate decoding functions for list of specification files in asn1/raw/carma_j2735 (this generates the conversion functions in stol_its_conversion )
    - `python3 utils/codegen/codegen-py/codeGeneration.py`





