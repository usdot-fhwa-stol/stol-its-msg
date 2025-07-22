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

def process_primitive(body,asn1_name,out_dir):
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

def process_sequence_of(body,asn1_name,asn1_types,asn1_raw,asn1_classes,out_dir):
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

        return {
            "element_name": validate_name(element_type),
            "struct_name": validate_name(asn1_name),
            "includes": includes
        }

    if element_type in asn1_definition_types:
        if element_type == "SEQUENCE":
            log_info(f"Processing SEQUENCE OF {name} with element type {element_type}")
            new_type=asn1_name+"__Member"
            res=process_sequence(element,new_type,asn1_types,asn1_raw,asn1_classes,out_dir)
            log_info(f"Rendering SEQUENCE OF for {asn1_name} with result: {res}")
            render_sequence(res,new_type,asn1_types,asn1_raw)
        else:
            sys.exit(f"Error: Unsupported SEQUENCE OF type {element_type} in {asn1_name}")

        return {
            "element_name": validate_name(element_type),
            "struct_name": validate_name(asn1_name),
            "includes": includes
        }
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
        sys.exit(f"Error: Unknown type in {asn1_name}")
        


def render_sequence_of(res,asn1_name,asn1_types,asn1_raw):
    c_s=process_comments(asn1_name,asn1_raw)
    log_info(f"Rendering SEQUENCE OF for {asn1_name} with comments: {c_s}")

    r_out={}

    rendered=templates["SEQUENCE_OF"].render(
        struct_name=validate_name(asn1_name),
        element_name=res['element_name'],
        includes=res['includes'],
        comments=c_s
    )

    r_out['src']={
        "file_name": f"{validate_name(asn1_name)}_converter.cpp",
        "content": rendered
    }

    rendered=templates["HEADER"].render(
        struct_name=validate_name(asn1_name),
        include_name=asn1_name,
        includes=res['includes']
    )

    r_out['header']={
        "file_name": f"{validate_name(asn1_name)}_converter.hpp",
        "content": rendered
    }

    return r_out

def process_ia5string(body,asn1_name,asn1_types,asn1_raw,out_dir):
    
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


    r_out={}

    rendered=templates["IA5STRING"].render(
        struct_name=validate_name(asn1_name),
        optional=res['code']['optional'],
        includes=res['includes'],
        comments=c_s
    )

    r_out['src']={
        "file_name": f"{validate_name(asn1_name)}_converter.cpp",
        "content": rendered
    }

    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        includes=res['includes']
    )

    r_out['header']={
        "file_name": f"{validate_name(asn1_name)}_converter.hpp",
        "content": rendered
    }

    return r_out

def process_bit_string(body,asn1_name,asn1_types,asn1_raw,out_dir):
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
    rendered=templates["BIT_STRING"].render(
        struct_name=validate_name(asn1_name),
        members=res['code']['members'],
        includes=res['includes'],
        comments=c_s
    )

    r_out={
        "src":{
            "file_name": f"{validate_name(asn1_name)}_converter.cpp",
            "content": rendered
        }
    }

    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        members=res['code']['members'],
        includes=res['includes']
    )

    r_out['header']={
        "file_name": f"{validate_name(asn1_name)}_converter.hpp",
        "content": rendered
    }

    return r_out


def process_enumerated(body,asn1_name,asn1_types,asn1_raw,out_dir):
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

    r_out={}

    rendered=templates["ENUMERATED"].render(
        struct_name=validate_name(asn1_name),
        members=res['code']['members'],
        includes=res['includes'],
        comments=c_s
    )
    r_out['src']={
        "file_name": f"{validate_name(asn1_name)}_converter.cpp",
        "content": rendered
    }

    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        members=res['code']['members'],
        includes=res['includes']
    )

    r_out['header']={
        "file_name": f"{validate_name(asn1_name)}_converter.hpp",
        "content": rendered
    }

    return r_out


def process_octet_string(body,asn1_name,asn1_types,asn1_raw,out_dir):
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

    r_out={}

    rendered=templates["OCTET_STRING"].render(
        struct_name=validate_name(asn1_name),
        includes=res['includes'],
        comments=c_s
    )
    r_out['src']={
        "file_name": f"{validate_name(asn1_name)}_converter.cpp",
        "content": rendered
    }
 
    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        includes=res['includes']
    )

    r_out['header']={
        "file_name": f"{validate_name(asn1_name)}_converter.hpp",
        "content": rendered
    }
  
    return r_out

def process_choice(body,asn1_name,asn1_types,asn1_raw,asn1_classes,out_dir):
    members=body['members']

    c_data=[]
    choices=[]
    includes=[]

    for member in members:
        if not member:
            continue
        
        member_type=member['type']
        member_name=member['name']

        if member_type in asn1_types:

            choices.append({
                "type":"simple",
                "name": validate_name(member_name),
                "struct_name": validate_name(member_type),
            })

            includes.append({
                "name": validate_name(member_type)+"_converter.hpp",
                "type": member_type
            })
        elif member_type in asn1_definition_types:
            custom_code=None
            if member_type=="SEQUENCE OF":
                res=process_sequence_of(member,member_name,asn1_types,asn1_raw, asn1_classes,out_dir)
                log_info(f"Rendering SEQUENCE OF in CHOICE for {member_name} with result: {res}")
                rendered=templates["convertSequenceOf"].render(
                    name=member_name,
                    choice_name="choice."+member_name,
                    element_name=res['element_name']
                )

                splits=rendered.split("### code break ###")
                rendered_json=splits[0]
                rendered_struct=splits[1]

                choices.append({
                    "type":"custom",
                    "custom_code":{
                        "json": rendered_json,
                        "struct": rendered_struct
                    },
                    "name": validate_name(member_name),
                    "struct_name": validate_name(member_name),
                })

                includes.append(*res['includes'])
            

    c_data.append({
        "struct_name":asn1_name,
        "choices":choices,
    })

    
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
    # log_info(f"Choices: {res['code'][0]['choices']}")

    r_out={}

    rendered=templates["CHOICE"].render(
        struct_name=validate_name(asn1_name),
        choices=res['code'][0]["choices"],
        includes=res['includes'],
        comments=c_s
    )

    r_out['src']={
        "file_name": f"{validate_name(asn1_name)}_converter.cpp",
        "content": rendered
    }

    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        choices=res['code'][0]["choices"],
        includes=res['includes']
    )

    r_out['header']={
        "file_name": f"{validate_name(asn1_name)}_converter.hpp",
        "content": rendered
    }

    return r_out

def process_sequence(body,asn1_name,asn1_types,asn1_raw,asn1_classes,out_dir):
    members=body['members']

    if "parameters" in body:
        parameters=body['parameters']
        if parameters[0]=="Set":
            return 

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
                res=process_choice(member,asn1_name,asn1_types, asn1_raw, asn1_classes,out_dir)
                log_info(f"Rendering CHOICE in SEQUENCE for {asn1_name} with result: {res}")

                choices=res['code'][0]["choices"]


                rendered_choice=templates["convertChoice"].render(
                    name=validate_name(member_name),
                    choices=choices,
                    struct_name=validate_name(struct_name),
                )

                splits=rendered_choice.split("### code break ###")
                rendered_json_choice=splits[0]
                rendered_struct_choice=splits[1]

                log_info(f"Rendered choice for {member_name}: {rendered_choice}")
                log_info(res['includes'])
                c_data.append({
                    "member_name": member_name,
                    "member_type": member_type,
                    "struct_name": struct_name,
                    "item_type": "custom",
                    "optional": member_is_optional,
                    "custom_code": {
                        "json": rendered_json_choice,
                        "struct":rendered_struct_choice
                    }
                })
                
                for inc in res['includes']:
                    if inc['name'] not in includes:
                        includes.append(inc)
                
                
            elif member_type=="SEQUENCE OF":
                element_type=member['element']['type']
                
                rendered_sequence_of=templates["convertSequenceOf"].render(
                    name=validate_name(member_name),
                    element_name=validate_name(element_type)
                )

                splits=rendered_sequence_of.split("### code break ###")
                rendered_json_sequence_of=splits[0]
                rendered_struct_sequence_of=splits[1]
                log_info(f"Rendered sequence of for {member_name}: {rendered_sequence_of}")
                c_data.append({
                    "member_name": member_name,
                    "member_type": member_type,
                    "struct_name": validate_name(struct_name),
                    "item_type": "custom",
                    "optional": member_is_optional,
                    "custom_code": {
                        "json": rendered_json_sequence_of,
                        "struct":rendered_struct_sequence_of
                    }
                })

                includes.append({
                    "name": validate_name(element_type)+"_converter.hpp",
                })
                includes.append({
                    "name": validate_name(element_type)+".h",
                })


            else:
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
    
    r_out={}

    rendered=templates["SEQUENCE"].render(
        struct_name=validate_name(asn1_name),
        members=res['code'],
        includes=res['includes'],
        comments=c_s
    )

    r_out['src']={
        "file_name": f"{validate_name(asn1_name)}_converter.cpp",
        "content": rendered
    }

    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        members=res['code'],
        includes=res['includes']
    )

    r_out['header']={
        "file_name": f"{validate_name(asn1_name)}_converter.hpp",
        "content": rendered
    }

    return r_out

def render_primitive(asn1_name,asn1_types,asn1_raw):

    c_s=process_comments(asn1_name,asn1_raw)
    rendered=templates["PRIMITIVES"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
        includes=[{
            "name": validate_name(asn1_name)+"_converter.hpp"
        }],
        comments=c_s
    )
    r_out={
        "src":{
            "file_name": f"{validate_name(asn1_name)}_converter.cpp",
            "content": rendered
        }
    }

    rendered=templates["HEADER"].render(
        include_name=asn1_name,
        struct_name=validate_name(asn1_name),
    )
    r_out['header']={
        "file_name": f"{validate_name(asn1_name)}_converter.hpp",
        "content": rendered
    }

    return r_out
   

def process_asn1_definitions(asn1_name,asn1_types,asn1_raw,asn1_classes,out_dir):
    body=asn1_types[asn1_name]
    d_type=body['type']
    log_info(f"Processing ASN.1 definition: {asn1_name} of type {d_type}")

    out=None
    if d_type=="SEQUENCE":
        res=process_sequence(body,asn1_name,asn1_types,asn1_raw,asn1_classes,out_dir)
        if not res:
            return
        out=render_sequence(res,asn1_name,asn1_types,asn1_raw)

    elif d_type=="SEQUENCE OF":
        res=process_sequence_of(body,asn1_name,asn1_types,asn1_raw, asn1_classes,out_dir)
        out=render_sequence_of(res,asn1_name,asn1_types,asn1_raw)

    elif d_type=="CHOICE":
        res=process_choice(body,asn1_name,asn1_types,asn1_raw,asn1_classes,out_dir)
        out=render_choice(res,asn1_name,asn1_types,asn1_raw)

    elif d_type=="IA5String":
        res=process_ia5string(body,asn1_name,asn1_types,asn1_raw,out_dir)
        out=render_ia5string(res,asn1_name,asn1_types,asn1_raw)

    elif d_type=="BIT STRING":
        res=process_bit_string(body,asn1_name,asn1_types,asn1_raw,out_dir)
        out=render_bit_string(res,asn1_name,asn1_types,asn1_raw)

    elif d_type=="ENUMERATED":
        res=process_enumerated(body,asn1_name,asn1_types,asn1_raw,out_dir)
        out=render_enumerated(res,asn1_name,asn1_types,asn1_raw)

    elif d_type=="OCTET STRING":
        res=process_octet_string(body,asn1_name,asn1_types,asn1_raw,out_dir)
        out=render_octet_string(res,asn1_name,asn1_types,asn1_raw)

    elif d_type in primitive_types:
        # print(f"Processing primitive type {d_type} for {asn1_name}")
        out=render_primitive(asn1_name,asn1_types,asn1_raw)

    if out:
        src_file_name=out['src']['file_name']
        header_file_name=out['header']['file_name']

        src_file_path=os.path.join(out_dir,src_file_name)
        header_file_path=os.path.join(out_dir,header_file_name)

        with open(src_file_path, "w") as f:
            f.write(out['src']['content'])
            log_info(f"Generated C code for {asn1_name} in {src_file_path}")

        with open(header_file_path, "w") as f:
            f.write(out['header']['content'])
            log_info(f"Generated C++ header for {asn1_name} in {header_file_path}")

def process_asn1_sets(asn1_name,asn1_types,asn1_raw,asn1_classes,asn1_sets,out_dir):
    body=asn1_sets[asn1_name]
    d_type=body['type']
    
    out=None
    if d_type=="SEQUENCE":
        res=process_sequence(body,asn1_name,asn1_types,asn1_raw,asn1_classes,out_dir)
        if not res:
            return
        out=render_sequence(res,asn1_name,asn1_types,asn1_raw)
    

    if out:
        src_file_name=out['src']['file_name']
        header_file_name=out['header']['file_name']

        src_file_path=os.path.join(out_dir,src_file_name)
        header_file_path=os.path.join(out_dir,header_file_name)

        with open(src_file_path, "w") as f:
            f.write(out['src']['content'])
            log_info(f"Generated C code for {asn1_name} in {src_file_path}")

        with open(header_file_path, "w") as f:
            f.write(out['header']['content'])
            log_info(f"Generated C++ header for {asn1_name} in {header_file_path}")



def generate_code(file_path,out_dir):
    files=[file_path]
    asn1_docs, asn1_raw = parseAsn1Files(files)
    asn1_types = extractAsn1TypesFromDocs(asn1_docs)
    asn1_values = extractAsn1ValuesFromDocs(asn1_docs)
    asn1_sets = extractAsn1SetsFromDocs(asn1_docs)
    asn1_classes = extractAsn1ClassesFromDocs(asn1_docs)


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
        process_asn1_definitions(key,asn1_types, asn1_raw, asn1_classes,out_dir)


    for key in asn1_sets:
        print(f"Processing ASN.1 set: {key}")
        asn1_sets[key]['type']="SEQUENCE"
        print(asn1_sets[key])

    for key, value in list(asn1_sets.items()):
        process_asn1_sets(key,asn1_types, asn1_raw, asn1_classes,asn1_sets,out_dir)
        


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
        spec_files=os.listdir("./asn1/raw/carma_j2735")

        for spec_file in spec_files:
            if not spec_file.endswith(".asn") and not spec_file.endswith(".asn1"):
                continue

            name=spec_file.split(".")[0]

            if not os.path.exists(os.path.join(output_dir, name)):
                os.makedirs(os.path.join(output_dir, name))

            print(f"Processing {spec_file} ...")
            file_path=os.path.join("./asn1/raw/carma_j2735",spec_file)
            final_output_dir=os.path.join(output_dir, name)
            generate_code(file_path,final_output_dir)


if __name__ == "__main__":
    main()