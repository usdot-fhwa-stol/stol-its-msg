# asn1-to-json

This project provides a set of tools to convert ASN.1 message definitions into JSON format using Jinja2 templates. It aims to facilitate the integration of ASN.1 data structures with modern applications that utilize JSON for data interchange.

## Project Structure

- `src/asn1ToJsonMsg.py`: Contains the logic for converting ASN.1 message definitions to JSON format.
- `src/utils/asn1CodeGenerationUtils.py`: Utility functions for ASN.1 code generation, including validation and type extraction.
- `src/templates/`: Contains Jinja2 templates for generating JSON output:
  - `JsonMessageType.json.jinja2`: Template for complete message types.
  - `JsonChoiceType.json.jinja2`: Template for choice types.
  - `JsonSequenceType.json.jinja2`: Template for sequence types.
- `tests/test_asn1ToJsonMsg.py`: Unit tests for the conversion logic.
- `requirements.txt`: Lists the required Python dependencies.

## Installation

To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Usage

To convert ASN.1 definitions to JSON, execute the `asn1ToJsonMsg.py` script with the appropriate arguments. Ensure that your ASN.1 files are correctly formatted and accessible.

## Running Tests

To run the unit tests for the conversion logic, use:

```
pytest tests/test_asn1ToJsonMsg.py
```

This will ensure that the conversion functions work as expected and that the generated JSON adheres to the defined formats.