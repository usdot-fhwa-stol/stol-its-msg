from asn1CodeGenerationUtils import *
from asn1ToConversionHeader import loadJinjaTemplates
import os
import logging
import sys
import shutil
import argparse


primitive_types=["INTEGER","BOOLEAN"]
asn1_definition_types=["SEQUENCE","SEQUENCE OF","CHOICE","IA5String","BIT STRING","OCTET STRING","ENUMERATED"]
c_keywords=["int","char","float","double","long","short","void","unsigned","signed","const","volatile","static","extern","register","inline"]

log_file = os.path.join(os.getcwd(), "codegen.log")
logging.basicConfig(
    filename=log_file,  # Log file path (in current directory)
    level=logging.DEBUG,  # Change to DEBUG if needed
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",  # Overwrite the log file on each run
)

def log_info(*args):
    logging.info(' '.join(map(str, args)))

def log_warning(message):
    logging.warning(message)

def log_error(message):
    logging.error(message)

def log_exception(e):
    logging.exception(e)

templates= loadJinjaTemplates()
tag="carma_j2735_"

name=""

def process_comments(asn1_name,asn1_raw):
    comments=None
    if asn1_name in asn1_raw:
        comments=asn1_raw[asn1_name]
    else:
        return []
    
    additional_comments=[
        "This file contains automatically generated C++ decoding functions using Jinja templates.",
        "Do not modify manually unless you know what you're doing.",
        "Below is the schema used to generate the functions:",
        "\n"
    ]

    c_s=[]
    if comments:
        c_s=comments.split("\n")
        c_s=[c for c in c_s]
    c_s=[*additional_comments, *c_s]
    comments="\n".join(c_s)

    return c_s

def process_primitive(body,asn1_name):
    if body['type'] == "INTEGER":
        if "restricted-to" in body:
            min_val=body["restricted-to"][0][0]
            max_val=body["restricted-to"][0][1]
            log_info(f"INTEGER: min: {min_val} max: {max_val}")
        else:
            log_warning(f"Error: is an INTEGER but has no restricted-to")

        return {
            "include_name": asn1_name,
            "struct_name": validate_name(asn1_name),
        }

    elif body["type"] == "BOOLEAN":
        res={
            "include_name": asn1_name,
            "struct_name": validate_name(asn1_name),
        }

        return res
    else:
        log_error(f"Error: Unsupported primitive type {body['type']}")
        return None

def process_sequence_of(body,asn1_name,asn1_types,asn1_raw,asn1_classes):
    element=body['element']
    element_type=element['type']

    name=body['name'] if 'name' in body else None
    size=body['size'][0]
    min_size=size[0]
    max_size=size[1]
    is_optional=body.get('optional', False)

    includes=[]
    if "actual-parameters" in element:
        includes.append({
            "name":element_type+".h"
        })
        element_type=element['actual-parameters'][0]['type']
        log_info(f"Element type for {asn1_name} is {element_type}")

    if element_type in asn1_definition_types:
        if element_type == "SEQUENCE":
            log_info(f"Processing SEQUENCE OF {name} with element type {element_type}")
            new_type=asn1_name+"__Member"
            res=process_sequence(element,new_type,asn1_types,asn1_raw,asn1_classes)
            render_sequence(res,new_type,asn1_types,asn1_raw)
        else:
            sys.exit(f"Error: Unsupported SEQUENCE OF type {element_type} in {asn1_name}")

    elif asn1_types[element_type]:
        includes=[{
            "name": validate_name(element_type)+"_converter.hpp",
        }]
        includes.append({
            "name": asn1_name+".h",
        })
        includes.append({
            "name":element_type+".h",
        })
        return {
            "element_name": validate_name(element_type),
            "struct_name": validate_name(asn1_name),
            "includes": includes
        }
        
    else:
        pass


def render_sequence_of(res,asn1_name,asn1_types,asn1_raw):
    c_s=process_comments(asn1_name,asn1_raw)
    log_info(f"Rendering SEQUENCE OF for {asn1_name} with comments: {c_s}")
    rendered=templates["SEQUENCE_OF"].render(
        struct_name=validate_name(asn1_name),
        element_name=res['element_name'],
        includes=res['includes'],
        comments=c_s
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.cpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C code for {asn1_name} in src/{validate_name(asn1_name)}_converter.cpp")
    rendered=templates["HEADER"].render(
        struct_name=validate_name(asn1_name),
        include_name=asn1_name,
        includes=res['includes']
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.hpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C++ header for {asn1_name} in include/{validate_name(asn1_name)}_converter.hpp")


def process_ia5string(body,asn1_name,asn1_types,asn1_raw):
    
    is_optional=body.get('optional', False)
    log_info(f"Processing IA5String {asn1_name}")

    c_data={
        "struct_name":asn1_name,
        
        "optional":is_optional
    }
    includes=[{
        "name": asn1_name+".h",
    }]

    includes.append({
        "name":validate_name(asn1_name)+"_converter.hpp",
    })

    return {
        "code":c_data,
        "includes":includes,
    }

def render_ia5string(res,asn1_name,asn1_types,asn1_raw):
    c_s=process_comments(asn1_name,asn1_raw)
    log_info(f"Rendering IA5String for {asn1_name} with comments: {c_s}")
    rendered=templates["IA5STRING_CPP"].render(
        struct_name=validate_name(asn1_name),
        optional=res['code']['optional'],
        includes=res['includes'],
        comments=c_s
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.cpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C code for {asn1_name} in src/{validate_name(asn1_name)}_converter.cpp")
    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        includes=res['includes']
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.hpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C++ header for {asn1_name} in include/{validate_name(asn1_name)}_converter.hpp")


def process_bit_string(body,asn1_name,asn1_types,asn1_raw):
    size=body['size'][0] if "size" in body else 0
    named_bits=body['named-bits'] if 'named-bits' in body else []

    members=[]
    for named_bit in named_bits:
        if not named_bit:
            continue
        member_name=named_bit[0]
        member_value=named_bit[1]
        members.append({
            "name": validate_name(member_name),
            "value": member_value
        })

    context={
        "struct_name": validate_name(asn1_name),
        "members": members,
        "optional": body.get('optional', False)
    }
    includes=[{
        "name": asn1_name+".h",
    }]

    includes.append({
        "name":validate_name(asn1_name)+"_converter.hpp",
    })



    return {
        "code": context,
        "includes": includes,
    }


def render_bit_string(res,asn1_name,asn1_types,asn1_raw):
    c_s=process_comments(asn1_name,asn1_raw)
        
    comments="\n".join(c_s)
    log_info(f"Rendering bit string for {asn1_name} with comments: {comments}")
    rendered=templates["BIT_STRING_CPP"].render(
        struct_name=validate_name(asn1_name),
        members=res['code']['members'],
        includes=res['includes'],
        comments=c_s
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.cpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C code for {asn1_name} in src/{validate_name(asn1_name)}_converter.cpp")
    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        members=res['code']['members'],
        includes=res['includes']
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.hpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C++ header for {asn1_name} in include/{validate_name(asn1_name)}_converter.hpp")


def process_enumerated(body,asn1_name,asn1_types,asn1_raw):
    values=body['values']
    members=[]
    for value in values:
        if not value:
            continue
        member_name=value[0]
        member_value=value[1]
        members.append({
            "name": validate_name(member_name),
            "value": member_value
        })

    context={
        "struct_name": validate_name(asn1_name),
        "members": members,
        "optional": body.get('optional', False)
    }
    includes=[{
        "name": asn1_name+".h",
    }]

    includes.append({
        "name":validate_name(asn1_name)+"_converter.hpp",
    })


    return {
        "code": context,
        "includes": includes,
    }

def render_enumerated(res,asn1_name,asn1_types,asn1_raw):
    c_s=process_comments(asn1_name,asn1_raw)

    
    log_info(f"Rendering enumerated for {asn1_name} with comments: {c_s}")
    rendered=templates["ENUMERATED_CPP"].render(
        struct_name=validate_name(asn1_name),
        members=res['code']['members'],
        includes=res['includes'],
        comments=c_s
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.cpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C code for {asn1_name} in src/{validate_name(asn1_name)}.cpp")

    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        members=res['code']['members'],
        includes=res['includes']
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.hpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C++ header for {asn1_name} in include/{validate_name(asn1_name)}.hpp")


def process_octet_string(body,asn1_name,asn1_types,asn1_raw):
    context={
        "struct_name": validate_name(asn1_name),
        "optional": body.get('optional', False)
    }

    includes=[{
        "name": asn1_name+".h",
    }]

    includes.append({
        "name":validate_name(asn1_name)+"_converter.hpp",
    })

    return {
        "code": context,
        "includes": includes,
    }


def render_octet_string(res,asn1_name,asn1_types,asn1_raw):
    c_s=process_comments(asn1_name,asn1_raw)

    log_info(f"Rendering octet string for {asn1_name} with comments: {c_s}")
    rendered=templates["OCTET_STRING_CPP"].render(
        struct_name=validate_name(asn1_name),
        includes=res['includes'],
        comments=c_s
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.cpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C code for {asn1_name} in src/{validate_name(asn1_name)}.c")
    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        includes=res['includes']
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.hpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C++ header for {asn1_name} in include/{validate_name(asn1_name)}.h")

def process_choice(body,asn1_name,asn1_types,asn1_raw):
    members=body['members']

    c_data=[]
    choices=[]
    for member in members:
        if not member:
            continue
        
        member_type=member['type']
        member_name=member['name']

        choices.append({
            "name": validate_name(member_name),
            "struct_name": validate_name(member_type),
        })

    c_data.append({
        "struct_name":asn1_name,
        "choices":choices,
    })

    includes=[]
    includes.append({
        "name": asn1_name+".h"
    })
    includes.append({
        "name":validate_name(asn1_name)+"_converter.hpp",
    })


    return {
        "code":c_data,
        "includes":includes,
    }


def render_choice(res,asn1_name,asn1_types,asn1_raw):
    c_s=process_comments(asn1_name,asn1_raw)

    log_info(f"Rendering choice for {asn1_name} with comments: {c_s}")
    log_info(f"Choices: {res['code'][0]['choices']}")
    rendered=templates["CHOICE_CPP"].render(
        struct_name=validate_name(asn1_name),
        choices=res['code'][0]["choices"],
        includes=res['includes'],
        comments=c_s
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.cpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C code for {asn1_name} in src/{validate_name(asn1_name)}_converter.cpp")
    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        choices=res['code'][0]["choices"],
        includes=res['includes']
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.hpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C++ header for {asn1_name} in include/{validate_name(asn1_name)}_converter.hpp")


def process_sequence(body,asn1_name,asn1_types,asn1_raw,asn1_classes):
    members=body['members']

    c_data=[]
    includes=[]
    for member in members:
        if not member:
            continue
        member_type=member['type']
        member_name=member['name']

        if member_name in c_keywords:
            member_name=member_name.capitalize()
        member_is_optional=member.get('optional', False)

        if member_type in asn1_definition_types:
            struct_name=validate_name(asn1_name)+"__"+member_name
            if member_type=="CHOICE":
                asn1_types[struct_name]=member
                process_asn1_definitions(struct_name,asn1_types, asn1_raw, asn1_classes)

            elif member_type=="SEQUENCE OF":
                pass

            c_data.append({
                "member_name": member_name,
                "member_type": member_type,
                "struct_name": struct_name,
                "item_type": "complex",
                "optional": member_is_optional
            })
            includes.append({
                "name": validate_name(struct_name)+"_converter.hpp",
                "type": member_type
            })
            pass
        elif member_type in asn1_classes:
            member_type=asn1_classes[member_type]
            c_data.append({
                "member_name": member_name,
                "member_type": member_type,
                "struct_name": validate_name(member_type),
                "item_type": "complex",
                "optional": member_is_optional
            })
        else:
            c_data.append({
                "member_name": member_name,
                "member_type": member_type,
                "struct_name": validate_name(member_type),
                "item_type": "complex",
                "optional": member_is_optional
            })

            includes.append({
                "name": validate_name(member_type)+"_converter.hpp",
            })
    includes.append({
        "name": asn1_name+".h"
    })

    includes.append({
        "name": validate_name(asn1_name)+"_converter.hpp",
    })

    includes_set=set()
    for inc in includes:
        if inc['name'] not in includes_set:
            includes_set.add(inc['name'])
    includes=[{"name": inc} for inc in includes_set]
    return {
        "code":c_data,
        "includes":includes,
    }

def render_sequence(res,asn1_name,asn1_types,asn1_raw):
    c_s=process_comments(asn1_name,asn1_raw)
    # print(res['includes'])
    rendered=templates["SEQUENCE_CPP"].render(
        struct_name=validate_name(asn1_name),
        members=res['code'],
        includes=res['includes'],
        comments=c_s
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.cpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C code for {asn1_name} in src/{validate_name(asn1_name)}_converter.cpp")

    rendered=templates["SEQUENCE_HPP"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        members=res['code'],
        includes=res['includes']
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.hpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C++ header for {asn1_name} in include/{validate_name(asn1_name)}_converter.hpp")


def render_primitive(asn1_name,asn1_types,asn1_raw):
    # print(f"Rendering primitive for {asn1_name}")
    c_s=process_comments(asn1_name,asn1_raw)
    rendered=templates["PRIMITIVES_CPP"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        includes=[{
            "name": validate_name(asn1_name)+"_converter.hpp"
        }],
        comments=c_s
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.cpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C code for {asn1_name} in src/{validate_name(asn1_name)}_converter.cpp")

    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
    )
    with open(f"./stol_its_conversion/{validate_name(asn1_name)}_converter.hpp", "w") as f:
        f.write(rendered)
        log_info(f"Generated C++ header for {asn1_name} in include/{validate_name(asn1_name)}_converter.hpp")


def process_asn1_definitions(asn1_name,asn1_types,asn1_raw,asn1_classes):
    body=asn1_types[asn1_name]
    d_type=body['type']
    log_info(f"Processing ASN.1 definition: {asn1_name} of type {d_type}")

    if d_type=="SEQUENCE":
        res=process_sequence(body,asn1_name,asn1_types,asn1_raw,asn1_classes)
        render_sequence(res,asn1_name,asn1_types,asn1_raw)

    elif d_type=="SEQUENCE OF":
        res=process_sequence_of(body,asn1_name,asn1_types,asn1_raw, asn1_classes)
        render_sequence_of(res,asn1_name,asn1_types,asn1_raw)

    elif d_type=="CHOICE":
        res=process_choice(body,asn1_name,asn1_types,asn1_raw)
        render_choice(res,asn1_name,asn1_types,asn1_raw)

    elif d_type=="IA5String":
        res=process_ia5string(body,asn1_name,asn1_types,asn1_raw)
        render_ia5string(res,asn1_name,asn1_types,asn1_raw)

    elif d_type=="BIT STRING":
        res=process_bit_string(body,asn1_name,asn1_types,asn1_raw)
        render_bit_string(res,asn1_name,asn1_types,asn1_raw)

    elif d_type=="ENUMERATED":
        res=process_enumerated(body,asn1_name,asn1_types,asn1_raw)
        render_enumerated(res,asn1_name,asn1_types,asn1_raw)

    elif d_type=="OCTET STRING":
        res=process_octet_string(body,asn1_name,asn1_types,asn1_raw)
        render_octet_string(res,asn1_name,asn1_types,asn1_raw)

    elif d_type in primitive_types:
        # print(f"Processing primitive type {d_type} for {asn1_name}")
        render_primitive(asn1_name,asn1_types,asn1_raw)


def generate_code(file_path):
    files=[file_path]
    name=os.path.basename(file_path).split("/")[-1].split(".")[0]
    asn1_docs, asn1_raw = parseAsn1Files(files)
    asn1_types = extractAsn1TypesFromDocs(asn1_docs)
    asn1_values = extractAsn1ValuesFromDocs(asn1_docs)
    asn1_sets = extractAsn1SetsFromDocs(asn1_docs)
    asn1_classes = extractAsn1ClassesFromDocs(asn1_docs)

    # asn1_types["OpenType"]={
    #     "type":"INTEGER",
    #     "restricted-to":[
    #         [0,1]
    #     ]
    # }

    """
        Parsing ASN1 Classes and Adjusting New Classes
    """
    new_classes={}
    for asn1_class in asn1_classes:
        info=asn1_classes[asn1_class]
        for member in info["members"]:
            if not member:
                log_error(f"Error: {asn1_class} has a None member")
                continue

            member_type=member["type"]
            member_name=member["name"]
            log_info(f"Member: {member_name} Type: {member_type}")


            if not member_type or not member_name:
                log_error(f"Error: {asn1_class} has a None member type or name")
                continue

            new_classes[f"{asn1_class}.{member_name}"]=member_type

    asn1_classes=new_classes

    

    for key,value in list(asn1_types.items()):

        process_asn1_definitions(key,asn1_types, asn1_raw, asn1_classes)


def parseCli():
    parser=argparse.ArgumentParser(
        description="ASN.1 to C code generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("-t", "--type", type=str, required=True, help="ASN1 type")

    args=parser.parse_args()

    return args


def main():

    # args=parseCli()

    #  make sure the stol_its_conversion directory exists
    output_dir = "./stol_its_conversion"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


    else:
    # if present, clear the directory and create two directories
        log_info(f"Clearing existing output directory: {output_dir}")
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                log_exception(f"Failed to delete {file_path}. Reason: {e}")

    
    spec_files=os.listdir("./asn1/raw/carma_j2735")

    for spec_file in spec_files:
        if not spec_file.endswith(".asn"):
            continue

        name=spec_file.split(".")[0]

        print(f"Processing {spec_file} ...")
        file_path=os.path.join("./asn1/raw/carma_j2735",spec_file)
        generate_code(file_path)


if __name__ == "__main__":
    main()