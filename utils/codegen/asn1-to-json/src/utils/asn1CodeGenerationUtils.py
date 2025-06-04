def validate_asn1_type(asn1_type):
    # Validate ASN.1 type structure
    if not isinstance(asn1_type, dict):
        raise ValueError("ASN.1 type must be a dictionary.")
    required_keys = ['name', 'type']
    for key in required_keys:
        if key not in asn1_type:
            raise ValueError(f"Missing required key: {key}")

def extract_asn1_types(asn1_docs):
    # Extract ASN.1 types from the provided documents
    asn1_types = {}
    for doc in asn1_docs:
        for type_name, type_info in doc.items():
            validate_asn1_type(type_info)
            asn1_types[type_name] = type_info
    return asn1_types

def valid_ros_type(type_name):
    # Convert ASN.1 type name to a valid ROS type name
    return type_name.replace('-', '_').replace(' ', '_')

def asn1_to_json_type(asn1_type):
    """Convert ASN.1 type to JSON schema type"""
    type_mapping = {
        'INTEGER': 'number',
        'BOOLEAN': 'boolean',
        'OCTET STRING': 'string',
        'UTF8String': 'string',
        'SEQUENCE': 'object',
        'CHOICE': 'object',
        'ENUMERATED': 'string'
    }
    return type_mapping.get(asn1_type, 'string')  # default to string if type not found