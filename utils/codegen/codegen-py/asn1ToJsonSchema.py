#!/usr/bin/env python3

import argparse
import glob
import os
from typing import Dict, List

import jinja2
from tqdm import tqdm

from asn1CodeGenerationUtils import *

def parseCli():
    """Parses script's CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Creates JSON schema files from ASN.1 definitions.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("files", type=str, nargs="+", help="ASN.1 files")
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="output directory")
    parser.add_argument("-t", "--type", type=str, required=True, help="ASN.1 type")

    return parser.parse_args()

def loadJinjaTemplate() -> jinja2.environment.Template:
    """Loads the jinja template for JSON schema files."""
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    return jinja_env.get_template("JsonSchemaType.json.jinja2")

def asn1TypeToJsonSchema(type_name: str, asn1_type: Dict, asn1_types: Dict[str, Dict], 
                        asn1_values: Dict[str, Dict], asn1_sets: Dict[str, Dict], 
                        asn1_classes: Dict[str, Dict], asn1_raw: Dict[str, str], 
                        jinja_template: jinja2.environment.Template) -> str:
    """Converts ASN.1 type to JSON schema."""
    jinja_context = asn1TypeToJinjaContext(type_name, asn1_type, asn1_types, 
                                         asn1_values, asn1_sets, asn1_classes)
    if jinja_context is None:
        return None

    if type_name in asn1_raw:
        jinja_context["asn1_definition"] = asn1_raw[type_name].rstrip("\n")
        
    return jinja_template.render(jinja_context)

def exportJsonSchema(json_schema: str, type_name: str, output_dir: str):
    """Exports a JSON schema file."""
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{type_name}.json")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json_schema)

def main():
    args = parseCli()

    # Parse ASN.1 files
    print("Parsing ASN.1 files ...")
    asn1_docs, asn1_raw = parseAsn1Files(args.files)
    asn1_types = extractAsn1TypesFromDocs(asn1_docs)
    asn1_values = extractAsn1ValuesFromDocs(asn1_docs)
    asn1_sets = extractAsn1SetsFromDocs(asn1_docs)
    asn1_classes = extractAsn1ClassesFromDocs(asn1_docs)

    checkTypeMembersInAsn1(asn1_types)

    # Generate JSON schema files
    jinja_template = loadJinjaTemplate()
    for type_name, asn1_type in (pbar := tqdm(asn1_types.items(), 
                                desc="Generating JSON schema files")):
        pbar.set_postfix_str(type_name)
        json_schema = asn1TypeToJsonSchema(type_name, asn1_type, asn1_types, 
                                         asn1_values, asn1_sets, asn1_classes, 
                                         asn1_raw, jinja_template)
        if json_schema:
            exportJsonSchema(json_schema, type_name, args.output_dir)

    print(f"Generated JSON schema files in {args.output_dir}")

if __name__ == "__main__":
    main()