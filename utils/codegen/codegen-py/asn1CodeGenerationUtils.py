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