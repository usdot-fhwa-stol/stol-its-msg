# etsi_its_messages
Create a folder named carma_j2734 under asn1/raw/ (i.e., asn1/raw/carma_j2734) and place the test ASN.1 file inside it. For example, we used TestMessage01.asn1 during testing.

# Running the Code Generator

```bash
# Navigate to the project root:
cd path\to\STOL-...  (your project folder)

# docker should be running to run this command successfully
python utils/codegen/asn1ToC/asn1ToC.py asn1/raw/carma_j2735/TestMessage01.asn -t carma_j2735 -o etsi_its_coding/etsi_its_carma_j2735_coding

# command to generate the corresponding JSON schema definitions for all ASN.1 specifications.
python utils\codegen\codegen-py\asn1ToRosMsg.py asn1\raw\carma_j2735\TestMessage01.asn -t carma_j2735 -o etsi_its_msgs\etsi_its_carma_j2735_msgs\msg

# command to auto-generates two functions: one to decode ASN.1 data to C structures, and another to convert C structures to JSON messages.
python utils\codegen\codegen-py\asn1ToConversionHeader.py asn1\raw\carma_j2735\TestMessage01.asn -t carma_j2735 -o etsi_its_conversion\etsi_its_carma_j2735_conversion\include\etsi_its_carma_j2735_conversion

```

