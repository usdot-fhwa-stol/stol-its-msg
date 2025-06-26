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

import logging
import re
import sys
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

def checkTypeMembersInAsn1(asn1_types: Dict[str, Dict]):
    """Checks if all type information is known and supported.

    This helps to check whether the types of all members of a type are also known.

    Args:
        asn1_types (Dict[str, Dict]): type information by type

    Raises:
        TypeError: if the type of a member is not part of the given types, hence unknown
    """

    # Get primitive types from type_mapping
    type_mapping = {
        'INTEGER': 'integer',
        'REAL': 'number',
        'BOOLEAN': 'boolean',
        'OCTET STRING': 'string',
        'UTF8String': 'string',
        'IA5String': 'string',
        'PrintableString': 'string',
        'SEQUENCE': 'object',
        'CHOICE': 'object', 
        'ENUMERATED': 'string',
        'BIT STRING': 'string',
        'SEQUENCE OF': 'array',
        'SET OF': 'array',
        'RAW': 'object'
    }

    known_types = ["SEQUENCE", "SEQUENCE OF", "CHOICE", "ENUMERATED", "NULL", "CPM-CONTAINER-ID-AND-TYPE.&id", "CPM-CONTAINER-ID-AND-TYPE.&Type"]
    known_types += list(asn1_types.keys())
    known_types += list(type_mapping.keys())

    # loop all types
    for asn1_type_name, asn1_type_info in asn1_types.items():

        # loop all members in type
        for member in asn1_type_info.get("members", []):

            if member is None:
                continue

            # list represents the asn1 extension "[[ ]]" notation
            if isinstance(member, list):
                for sub_member in member:
                    if sub_member["type"] not in known_types:
                        raise TypeError(
                            f"Type '{sub_member['type']}' of member '{sub_member['name']}' "
                            f"in '{asn1_type_name}' is undefined")
                continue

            if "components-of" in member:
                member["type"] = member["components-of"]

            # check if type is known
            if member["type"] not in known_types:
                if ".&" in member["type"]: # class type is currently just handled for CPM
                    logging.warning(
                        f"Type '{member['type']}' of member '{member['name']}' "
                        f"in '{asn1_type_name}' seems to relate to a 'CLASS' type, not "
                        f"yet supported")
                else:
                    raise TypeError(
                        f"Type '{member['type']}' of member '{member['name']}' "
                        f"in '{asn1_type_name}' is undefined")

def asn1_to_json_type(asn1_type: str) -> str:
    """Convert ASN.1 type to JSON schema type."""
    type_mapping = {
        'INTEGER': 'integer',
        'REAL': 'number',
        'BOOLEAN': 'boolean',
        'OCTET STRING': 'string',
        'UTF8String': 'string',
        'IA5String': 'string',
        'PrintableString': 'string',
        'SEQUENCE': 'object',
        'CHOICE': 'object',
        'ENUMERATED': 'string',
        'BIT STRING': 'string',
        'SEQUENCE OF': 'array',
        'SET OF': 'array', # Add SET OF
        'RAW': 'object' # Add RAW
    }
    return type_mapping.get(asn1_type, 'string')

def asn1TypeToJinjaContext(type_name: str, asn1_type: Dict, asn1_types: Dict[str, Dict],
                          asn1_values: Dict[str, Dict], asn1_sets: Dict[str, Dict],
                          asn1_classes: Dict[str, Dict]) -> Dict:
    """Convert ASN.1 type to Jinja context for JSON schema."""
    
    # Add debug logging
    print(f"Debug: Processing type {type_name}")
    print(f"Debug: ASN.1 type content: {asn1_type}")

    # Check if asn1_type is None
    if asn1_type is None:
        print(f"Warning: ASN.1 type is None for {type_name}")
        return None

    context = {
        'type_name': type_name,
        'type': asn1_type.get('type'),
        'json_type': asn1_to_json_type(asn1_type.get('type'))
    }

    if asn1_type.get('type') == 'SEQUENCE':
        context['properties'] = {}
        context['required'] = []
        
        # Check if members exist
        members = asn1_type.get('members', [])
        if not members:
            print(f"Warning: No members found for SEQUENCE {type_name}")
            return context

        for field in members:
            # Check if field is None
            if field is None:
                print(f"Warning: Encountered None field in {type_name}")
                continue
                
            # Check if field is a valid dictionary with required keys
            if not isinstance(field, dict) or 'type' not in field:
                print(f"Warning: Invalid field structure in {type_name}: {field}")
                continue

            field_info = {
                'type': asn1_to_json_type(field['type']),
                'description': field.get('description', '')
            }
            if 'constraints' in field:
                field_info['constraints'] = field['constraints']
            
            field_name = field.get('name')
            if field_name:
                context['properties'][field_name] = field_info
                if not field.get('optional', False):
                    context['required'].append(field_name)

    elif asn1_type.get('type') == 'ENUMERATED':
        context['enum'] = [v['name'] for v in asn1_type.get('values', [])]
    
    elif asn1_type.get('type') == 'CHOICE':
        context['oneOf'] = []
        for choice in asn1_type.get('members', []):
            if choice and 'type' in choice:
                choice_info = {
                    'type': asn1_to_json_type(choice['type']),
                    'description': choice.get('description', '')
                }
                context['oneOf'].append(choice_info)

    return context