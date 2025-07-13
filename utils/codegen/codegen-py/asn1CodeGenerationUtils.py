# ==============================================================================
# MIT License
#
# Copyright (c) 2023-2025 Institute for Automotive Engineering (ika), RWTH Aachen University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================


from typing import Dict, List, Optional, Tuple

import asn1tools
import numpy as np

def validateAsn1Type(asn1_type: Dict):
    """Validate ASN.1 type structure."""
    if not isinstance(asn1_type, dict):
        raise ValueError("ASN.1 type must be a dictionary.")
    required_keys = ['name', 'type']
    for key in required_keys:
        if key not in asn1_type:
            raise ValueError(f"Missing required key: {key}")

def validate_name(name):
    return name.replace(" ","_").replace("-","_")

def parseAsn1Files(files: List[str]) -> Tuple[Dict, Dict[str, str]]:
    """Parses ASN1 files.

    Args:
        files (List[str]): filepaths

    Returns:
        Tuple[Dict, Dict[str, str]]: parsed type information by document, raw string definition by type
    """

    asn1_raw = {}
    for file in files:
        with open(file) as f:
            lines = f.readlines()
        raw_def = None
        for line_idx, line in enumerate(lines):
            if "::=" in line:
                comment_lines = []
                for rline in reversed(lines[:line_idx]):
                    if rline.strip().endswith("*/"):
                        comment_lines.append(rline)
                    elif len(comment_lines) > 0:
                        comment_lines.append(rline)
                    if rline.strip().startswith("/**"):
                        comment_lines = reversed(comment_lines)
                        break
                if line.rstrip().endswith("{"):
                    type = line.split("::=")[0].split("{")[0].strip().split()[0]
                    raw_def = ""
                elif len(line.split("::=")) == 2:
                    type = line.split("::=")[0].strip().split()[0]
                    if "}" in line or not ("{" in line or "}" in line):
                        raw_def = line
                        asn1_raw[type] = "".join(comment_lines) + raw_def
                        raw_def = None
                    else:
                        raw_def = ""
            if raw_def is not None:
                raw_def += line
                # TODO: improve this condition
                if "}" in line and not "}," in line and not "} |" in line and not "} )" in line and not "})" in line and not ("::=" in line and line.rstrip().endswith("{")):
                    asn1_raw[type] = "".join(comment_lines) + raw_def
                    raw_def = None

    asn1_docs = asn1tools.parse_files(files)

    return asn1_docs, asn1_raw

def docForAsn1Type(asn1_type: str, asn1_docs: Dict) -> Optional[str]:
    """Finds the ASN1 document where a specific type is defined.

    Args:
        asn1_type (str): type name
        asn1_docs (Dict): parsed type information by document (from `parseAsn1Files`)

    Returns:
        Optional[str]: document name where type is defined, `None` if not found
    """

    for doc, asn1 in asn1_docs.items():
        if asn1_type in asn1["types"]:
            return doc

    return None

def extractAsn1TypesFromDocs(asn1_docs: Dict) -> Dict[str, Dict]:
    """Extracts all parsed ASN1 type information from multiple ASN1 documents.

    Args:
        asn1_docs (Dict): type information by document

    Raises:
        ValueError: if a type is found in multiple documents

    Returns:
        Dict[str, Dict]: type information by type
    """

    asn1_types = {}
    for doc, asn1 in asn1_docs.items():
        for type in asn1["types"]:
            if type not in asn1_types:
                asn1_types[type] = asn1["types"][type]
            else:
                raise ValueError(f"Type '{type}' from '{doc}' is a duplicate")

    return asn1_types

def extractAsn1ValuesFromDocs(asn1_docs: Dict) -> Dict[str, Dict]:
    """Extracts all parsed ASN1 value information from multiple ASN1 documents.

    Args:
        asn1_docs (Dict): type information by document

    Raises:
        ValueError: if a type is found in multiple documents

    Returns:
        Dict[str, Dict]: value information by name
    """

    asn1_values = {}
    for doc, asn1 in asn1_docs.items():
        for value in asn1["values"]:
            if value not in asn1_values:
                asn1_values[value] = asn1["values"][value]
            else:
                raise ValueError(f"Value '{value}' from '{doc}' is a duplicate")

    return asn1_values

def extractAsn1ClassesFromDocs(asn1_docs: Dict) -> Dict[str, Dict]:
    """Extracts all parsed ASN1 class information from multiple ASN1 documents.

    Args:
        asn1_docs (Dict): type information by document

    Raises:
        ValueError: if a class is found in multiple documents

    Returns:
        Dict[str, Dict]: class information by name
    """

    asn1_classes = {}
    for doc, asn1 in asn1_docs.items():
        for class_name in asn1["object-classes"]:
            if class_name not in asn1_classes:
                asn1_classes[class_name] = asn1["object-classes"][class_name]
            else:
                raise ValueError(f"Class '{class_name}' from '{doc}' is a duplicate")

    return asn1_classes

def extractAsn1SetsFromDocs(asn1_docs: Dict) -> Dict[str, Dict]:
    """Extracts all parsed ASN1 set information from multiple ASN1 documents.

    Args:
        asn1_docs (Dict): type information by document

    Raises:
        ValueError: if a set is found in multiple documents

    Returns:
        Dict[str, Dict]: set information by name
    """

    asn1_sets = {}
    for doc, asn1 in asn1_docs.items():
        for set_name in asn1["object-sets"]:
            if set_name not in asn1_sets:
                asn1_sets[set_name] = asn1["object-sets"][set_name]
            else:
                raise ValueError(f"Set '{set_name}' from '{doc}' is a duplicate")

    return asn1_sets



