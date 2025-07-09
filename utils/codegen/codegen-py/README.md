## Steps to generate decoding functions

### Prerequisites

- Make sure docker daemon is up and running
- Make sure BasicSafetyMessage.asn is present in asn1/raw/carma_j2735

### Steps

- Create a python environment
    - `python3 -m venv venv`
    - `. ./venv/bin/activate` for mac os

- To generate .c and .h files for a given specification file
    - `python3 utils/codegen/asn1ToC/asn1ToC.py asn1/raw/carma_j2735/BasicSafetyMessage.asn -t carma_j2735 -o stol_its_coding`

- To generate decoding functions for a given specification file
    - `python3 utils/codegen/codegen-py/codeGeneration.py`

