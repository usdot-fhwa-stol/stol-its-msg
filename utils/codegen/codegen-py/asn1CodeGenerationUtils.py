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

from typing import Dict, List, Tuple
import os
import glob
import re

def validateAsn1Type(asn1_type: Dict):
    """Validate ASN.1 type structure."""
    if not isinstance(asn1_type, dict):
        raise ValueError("ASN.1 type must be a dictionary.")
    required_keys = ['name', 'type']
    for key in required_keys:
        if key not in asn1_type:
            raise ValueError(f"Missing required key: {key}")

def extractAsn1TypesFromDocs(asn1_docs: List[str]) -> Dict[str, Dict]:
    """Extract ASN.1 types from the provided documents."""
    asn1_types = {}
    for doc in asn1_docs:
        for type_name, type_info in doc.items():
            validateAsn1Type(type_info)
            asn1_types[type_name] = type_info
    return asn1_types

def extractAsn1ValuesFromDocs(asn1_docs: List[str]) -> Dict[str, Dict]:
    """Extract ASN.1 values from the provided documents."""
    asn1_values = {}
    for doc in asn1_docs:
        for value_name, value_info in doc.get("values", {}).items():
            asn1_values[value_name] = value_info
    return asn1_values

def extractAsn1SetsFromDocs(asn1_docs: List[str]) -> Dict[str, Dict]:
    """Extract ASN.1 sets from the provided documents."""
    asn1_sets = {}
    for doc in asn1_docs:
        for set_name, set_info in doc.get("sets", {}).items():
            asn1_sets[set_name] = set_info
    return asn1_sets

def extractAsn1ClassesFromDocs(asn1_docs: List[str]) -> Dict[str, Dict]:
    """Extract ASN.1 classes from the provided documents."""
    asn1_classes = {}
    for doc in asn1_docs:
        for class_name, class_info in doc.get("classes", {}).items():
            asn1_classes[class_name] = class_info
    return asn1_classes

def parseAsn1Files(asn1_files: List[str]) -> Tuple[List[Dict], Dict[str, str]]:
    """Parse ASN.1 files and return a list of dictionaries and raw ASN.1 definitions."""
    asn1_docs = []
    asn1_raw = {}
    for asn1_file in asn1_files:
        with open(asn1_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract type definitions
            type_matches = re.finditer(r"([A-Z][a-zA-Z0-9]+ ::= [^\n]*?::=[\s\S]*?)(?=(^[A-Z][a-zA-Z0-9]+ ::=)|$)", content, re.MULTILINE)
            for match in type_matches:
                type_def = match.group(1).strip()
                type_name = type_def.split(" ::= ")[0].strip()
                asn1_raw[type_name] = type_def
                asn1_docs.append({type_name: {"name": type_name, "type": "RAW"}})  # Simplified for demonstration

    return asn1_docs, asn1_raw

def checkTypeMembersInAsn1(asn1_types: Dict[str, Dict]):
    """Check type members in ASN.1 types."""
    for type_name, asn1_type in asn1_types.items():
        if asn1_type['type'] == "SEQUENCE":
            if 'members' not in asn1_type:
                raise ValueError(f"Missing members in SEQUENCE {type_name}")

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
        'SEQUENCE OF': 'array'
    }
    return type_mapping.get(asn1_type, 'string')

def asn1TypeToJinjaContext(type_name: str, asn1_type: Dict, asn1_types: Dict[str, Dict],
                          asn1_values: Dict[str, Dict], asn1_sets: Dict[str, Dict],
                          asn1_classes: Dict[str, Dict]) -> Dict:
    """Convert ASN.1 type to Jinja context for JSON schema."""
    context = {
        'type_name': type_name,
        'type': asn1_type.get('type'),
        'json_type': asn1_to_json_type(asn1_type.get('type'))
    }

    if asn1_type.get('type') == 'SEQUENCE':
        context['fields'] = []
        context['required_fields'] = []
        for field in asn1_type.get('fields', []):
            field_info = {
                'name': field['name'],
                'json_type': asn1_to_json_type(field['type']),
                'description': field.get('description', '')
            }
            if 'constraints' in field:
                field_info['constraints'] = field['constraints']
            context['fields'].append(field_info)
            if not field.get('optional', False):
                context['required_fields'].append(field['name'])

    elif asn1_type.get('type') == 'ENUMERATED':
        context['enum_values'] = [v['name'] for v in asn1_type.get('values', [])]

    return context