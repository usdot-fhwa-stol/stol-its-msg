from asn1CodeGenerationUtils import *
from jinja2 import Environment, FileSystemLoader
from asn1ToConversionHeader import loadJinjaTemplates
import json
import logging
import os

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




name="TestMessage01"
file_path=f"./asn1/raw/carma_j2735/{name}.asn"
files=[file_path]

asn1_docs, asn1_raw = parseAsn1Files(files)
asn1_types = extractAsn1TypesFromDocs(asn1_docs)
asn1_values = extractAsn1ValuesFromDocs(asn1_docs)
asn1_sets = extractAsn1SetsFromDocs(asn1_docs)
asn1_classes = extractAsn1ClassesFromDocs(asn1_docs)


"""
    Loading templates and setting up the environment
"""
log_info("Loading templates")


templates=loadJinjaTemplates()


"""

Possible types of ASN.1 files:
SEQUENCE, SEQUENCE OF, OCTET STRING, INTEGER, ENUMERATED,BOOLEAN, BIT STRING

"""
primitive_types=["INTEGER","BIT STRING","OCTET STRING","ENUMERATED","BOOLEAN"]
complex_types=["SEQUENCE","SEQUENCE OF","CHOICE","IA5String"]
c_keywords=["int","char","float","double","long","short","void","unsigned","signed","const","volatile","static","extern","register","inline"]


def int_type(min_val,max_val):
    log_info(f"int_type: {min_val} {max_val}")
    if min_val is None or max_val is None:
        log_error(f"Error: min_val or max_val is None : {min_val} , {max_val}")
    if min_val >= 0:
        if max_val <= 255:
            return 'uint8_t'
        elif max_val <= 65535:
            return 'uint16_t'
        elif max_val <= 4294967295:
            return 'uint32_t'
        else:
            return 'uint64_t'
    else:
        if min_val >= -128 and max_val <= 127:
            return 'int8_t'
        elif min_val >= -32768 and max_val <= 32767:
            return 'int16_t'
        elif min_val >= -2147483648 and max_val <= 2147483647:
            return 'int32_t'
        else:
            return 'int64_t'
        

def validate_name(name):
    return name.replace(" ","_").replace("-","_")

def process_primitive(asn1_name,asn1_info,code):
    log_info(f"Processing primitive: {asn1_name} {asn1_info['type']}")
    if asn1_info["type"] == "INTEGER":
        if "restricted-to" in asn1_info:
            min_val=asn1_info["restricted-to"][0][0]
            max_val=asn1_info["restricted-to"][0][1]
            log_info(f"INTEGER: {asn1_name} min: {min_val} max: {max_val}")

        else:
            log_warning(f"Error: {asn1_name} is an INTEGER but has no restricted-to")

        context={
            "type":"simple",
            "asn1_type":int_type(min_val,max_val),
            "struct_name":asn1_name,
            # "data_type":"(double)",
            "function_name":"cJSON_AddNumberToObject"
        }
        log_info(f"INTEGER: {asn1_name} context: {context}")
        
        return context

    elif asn1_info["type"] == "BIT STRING":
        size=asn1_info["size"][0] if "size" in asn1_info else 0
        named_bits=asn1_info["named-bits"] if "named-bits" in asn1_info else []
        log_info(f"BIT STRING: {asn1_name} size: {size} named-bits: {named_bits}")
        c_type=""
        if size>=1 and size<=8:
            c_type="uint8_t"
        elif size>=9 and size<=16:
            c_type="uint16_t"
        elif size>=17 and size<=32:
            c_type="uint32_t"
        elif size>=33 and size<=64:
            c_type="uint64_t"
        else:
            log_error(f"Error: {asn1_name} is a BIT STRING but has an invalid size: {size}")
        
        members=[]
        for named_bit in named_bits:
            if not named_bit:
                log_error(f"Error: {asn1_name} has a None named bit")
                continue
            
            bit_name=named_bit[0]
            bit_index=named_bit[1]

            members.append({
                "name":validate_name(bit_name),
                "index":bit_index,
            })
            

        context={
            "struct_name":asn1_name,
            "c_type":c_type,
            "members":members,
        }

        log_info(f"BIT STRING: {asn1_name} context: {context}")

        render_def=templates["BIT_STRING"].render(context)

        code.append({
            "type":"code",
            "name":asn1_name,
            "code":render_def
        })

        code.append({
            "type":"include",
            "name":asn1_name,
            "include":f"{asn1_name}.h"
        })

        return {
            "type":"complex",
            "struct_name":validate_name(asn1_info['type']),
            "asn1_type":asn1_name.capitalize(),
            "function_name":"cJSON_AddItemToObject"
        }

    elif asn1_info["type"] == "ENUMERATED":
        vals=asn1_info["values"] if "values" in asn1_info else []

        members=[]
        for val in vals:
            if not val:
                log_warning(f"Error: {asn1_name} has a None value")
                continue

            val_name=val[0]
            val_value=val[1]

            members.append({
                "name":val_name,
                "index":val_value,
            })

        context={
            "struct_name":asn1_name,
            "members":members,
        }
        log_info(f"ENUMERATED: {asn1_name} members context: {context}")
        render_def=templates["ENUMERATED"].render(context)
        code.append({
            "type":"code",
            "name":asn1_name,
            "code":render_def
        })

        code.append({
            "type":"include",
            "name":asn1_name,
            "include":f"{asn1_name}"
        })

        res={
            "type":"complex",
            "struct_name":validate_name(asn1_name),
            "function_name":"cJSON_AddItemToObject"
        }

        log_info(f"ENUMERATED: {asn1_name} res: {res}")

        return res

    elif asn1_info["type"] == "OCTET STRING":
        size_len=len(asn1_info["size"])
        min=None
        max=None
        if size_len==1:
            pass
        elif size_len==2:
            pass
        else:
            log_error(f"Error: {asn1_name} is an OCTET STRING but has an invalid size: {size_len}")


        rendered=templates["OCTET_STRING"].render({
            "struct_name":asn1_name,
        })

        code.append({
            "type":"code",
            "name":asn1_name,
            "code":rendered
        })
        code.append({
            "type":"include",
            "name":asn1_name,
            "include":f"{asn1_name}.h"
        })
        res={
            "type":"complex",
            "asn1_type":"char*",
            "struct_name":validate_name(asn1_name),
            "function_name":"cJSON_AddItemToObject"
        }
        log_info(f"OCTET STRING: {asn1_name} res: {res}")
        return res

    elif asn1_info["type"] == "BOOLEAN":
        res={
            "type":"simple",
            "asn1_type":"bool",
            "struct_name":validate_name(asn1_name),
            # "data_type":"(cJSON_bool)",
            "function_name":"cJSON_AddBoolToObject"
        }

        log_info(f"BOOLEAN: {asn1_name} res: {res}")

        return res
    
    
    
    else:
        log_error(f"Error: {asn1_name} is an unknown type: {asn1_info['type']}")



def process_complex(asn1_name,asn1_info,asn1_types,asn1_values,asn1_classes,code):
    log_info(f"Processing complex: {asn1_name} {asn1_info['type']}")
    if asn1_info['type']=="SEQUENCE":
        out=[]
        for member in asn1_info["members"]:
            if not member:
                log_warning(f"Error: {asn1_name} has a None member")
                continue

            member_type=member["type"]
            member_name=member["name"]

            if member_name in c_keywords:
                member_name=member_name[0].upper()+member_name[1:]

            member_optional=member["optional"] if "optional" in member else False
            log_info(f"Member: {member_name} Type: {member_type} Optional: {member_optional}")

            if member_type in asn1_classes:
                log_info(f"Member: {member_name} Type: {member_type} is a class")
                member_type=asn1_classes[member_type]


            if member_type in primitive_types:
                log_info(f"Member: {member_name} Type: {member_type} is a primitive")
                res=process_primitive(member_name,member,code)
                log_info(f"Member: {member_name} Type: {member_type} res: {res}")

            elif member_type in complex_types:
                log_info(f"Member: {member_name} Type: {member_type} is a complex")
                res=process_complex(member_name,member,asn1_types,asn1_values,asn1_classes,code)
                log_info(f"Member: {member_name} Type: {member_type} res: {res}")
            else:
                log_info(f"Member: {member_name} Type: {member_type} is one of type")
                res=rec(member_type,asn1_types[member_type],asn1_types,asn1_values,asn1_classes,code)
                log_info(f"Member: {member_name} Type: {member_type} res: {res}")

            if res:
                if member_optional:
                    res["is_optional"]=True
                else:
                    res["is_optional"]=False

                res['struct_type']=member_type
                res['name']=member_name
                out.append(res)
        

        context={
            "struct_name":validate_name(asn1_name),
            "asn1_type":asn1_name.capitalize(),
            "members":out,
        }

        log_info(f"SEQUENCE: {asn1_name} context: {context}")

        rendered=templates["SEQUENCE"].render(context)


        code.append({
            "type":"code",
            "name":asn1_name,
            "code":rendered
        })

        code.append({
            "type":"include",
            "name":asn1_name,
            "include":f"{asn1_name}.h"
        })

        res={
            "type":"complex",
            "struct_name":validate_name(asn1_name),
            "asn1_type":asn1_info,
            "function_name":"cJSON_AddItemToObject",
        }
        log_info(f"SEQUENCE: {asn1_name} res: {res}")

        return res

    elif asn1_info['type']=="SEQUENCE OF":
        log_info(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}")
        element=asn1_info["element"]
        size=asn1_info["size"]
        min_size=size[0][0]
        max_size=size[0][1]
        log_info(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element} min_size: {min_size} max_size: {max_size}")

        if "name" in asn1_info:
            name=asn1_info["name"]
            log_info(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: name {name}")

        if "optional" in asn1_info:
            optional=asn1_info["optional"]
            

        if element['type'] in primitive_types:
            log_info(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} is a primitive")
            res=process_primitive(name,element)
            log_info(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} res: {res}")

        if element['type'] in complex_types:
            log_info(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} is a complex")
            res=process_complex("",element,asn1_types,asn1_values,asn1_classes,code)
            log_info(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} res: {res}")
        
        if element['type'] in asn1_types:
            log_info(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} is one of type")
            res=rec(asn1_name,asn1_types[element["type"]],asn1_types,asn1_values,asn1_classes,code)
            log_info(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} res: {res}")

        log_info(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} res: {res}")


        # rendered=templates["SEQUENCE_OF"].render(res)
        # code.append({
        #     "type":"code",
        #     "name":asn1_name,
        #     "code":rendered
        # })
        # code.append({
        #     "type":"include",
        #     "name":asn1_name,
        #     "include":f"{asn1_name}.h"
        # })
        # log_info(f"SEQUENCE OF: {asn1_name} {asn1_info['type']} res :  {res}")



        return {
            "type":"complex",
            "struct_name":validate_name(asn1_name),
            "asn1_type":asn1_info,
            "function_name":"cJSON_AddItemToObject",
            "element_type":res["struct_name"],
            "min_size":min_size,
            "max_size":max_size,
            "is_optional":optional if "optional" in asn1_info else False
        }
        

    elif asn1_info["type"] == "IA5String":
        

        context={
            "struct_name":validate_name(asn1_name),
            "asn1_type":asn1_name,
            "function_name":"cJSON_AddItemToObject",
        }

        rendered=templates["IA5String"].render(context)

        code.append({
            "type":"code",
            "name":asn1_name,
            "code":rendered
        })
        code.append({
            "type":"include",
            "name":asn1_name,
            "include":f"{asn1_name}.h"
        })

        res={
            "type":"complex",
            "asn1_type":"char*",
            "struct_name":validate_name(asn1_name),
            "function_name":"cJSON_AddItemToObject"
        }

        log_info(f"IA5String: {asn1_name} res: {res}")

        return res

    elif asn1_info["type"] == "CHOICE":
        log_info(f"CHOICE: {asn1_name} {asn1_info['type']}")
        out=[]
        for member in asn1_info["members"]:
            if not member:
                log_warning(f"Error: {asn1_name} has a None member")
                continue

            member_type=member["type"]
            member_name=member["name"]

            if member_name in c_keywords:
                member_name=member_name[0].upper()+member_name[1:]

            log_info(f"Member: {member_name} Type: {member_type}")

            if member_type in asn1_classes:
                log_info(f"Member: {member_name} Type: {member_type} is a class")
                member_type=asn1_classes[member_type]


            if member_type in primitive_types:
                log_info(f"Member: {member_name} Type: {member_type} is a primitive")
                res=process_primitive(member_name,member,code)
                log_info(f"Member: {member_name} Type: {member_type} res: {res}")

            elif member_type in complex_types:
                log_info(f"Member: {member_name} Type: {member_type} is a complex")
                res=process_complex(member_name,member,asn1_types,asn1_values,asn1_classes,code)
                log_info(f"Member: {member_name} Type: {member_type} res: {res}")
            else:
                log_info(f"Member: {member_name} Type: {member_type} is one of type")
                res=rec(member_type,asn1_types[member_type],asn1_types,asn1_values,asn1_classes,code)
                log_info(f"Member: {member_name} Type: {member_type} res: {res}")

            if res:
                res['struct_type']=member_type
                res['name']=member_name
                out.append(res)
        

        context={
            "struct_name":asn1_name,
            "asn1_type":asn1_name.capitalize(),
            "members":out,
        }

        log_info(f"CHOICE: {asn1_name} context: {context}")

        rendered=templates["CHOICE"].render(context)


        code.append({
            "type":"code",
            "name":asn1_name,
            "code":rendered
        })
        code.append({
            "type":"include",
            "name":asn1_name,
            "include":f"{asn1_name}.h"
        })

        res={
            "type":"complex",
            "struct_name":validate_name(asn1_name),
            "asn1_type":asn1_info,
            "function_name":"cJSON_AddItemToObject",
        }
        log_info(f"CHOICE: {asn1_name} res: {res}")
        return res

        

def rec(asn1_name,asn1_info,asn1_types,asn1_values,asn1_classes,code):
    log_info(f"Recursing: {asn1_name} {asn1_info['type']}")
    if asn1_info["type"] in primitive_types:
        log_info(f"Primitive: {asn1_name} {asn1_info['type']}")
        return process_primitive(asn1_name,asn1_info,code)
        
    if asn1_info["type"] in complex_types:
        log_info(f"Complex: {asn1_name} {asn1_info['type']}")
        return process_complex(asn1_name,asn1_info,asn1_types,asn1_values,asn1_classes,code)


    if asn1_info['type'] in asn1_types:
        log_info(f"ASN1: {asn1_name} {asn1_info['type']}")
        obj=asn1_types[asn1_info['type']]
        struct_type=asn1_info['type']
        res=rec(asn1_name,obj,asn1_types,asn1_values,asn1_classes,code)
        if res:
            res['struct_type']=struct_type
        log_info(f"ASN1: {asn1_name} {asn1_info['type']} res: {res}")
        return res
    
    if asn1_info['type'] in asn1_classes:
        log_info(f"ASN1 CLASS: {asn1_name} {asn1_info['type']}")
        obj_type=asn1_classes[asn1_info['type']]
        res=rec(asn1_name,asn1_types[obj_type],asn1_types,asn1_values,asn1_classes,code)
        log_info(f"ASN1 CLASS: {asn1_name} {asn1_info['type']} res: {res}")
        return res


"""
    parsing asn1 classes
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
log_info(f"ASN1 Classes: {asn1_classes}")

code=[]
res=rec(list(asn1_types.keys())[0],asn1_types[list(asn1_types.keys())[0]],asn1_types,asn1_values,asn1_classes,code)
log_info(f"Result: {res}")


code_file="""
#include <stdio.h>
#include <stdlib.h>
#include <cjson/cJSON.h>
#include "asn_application.h"      // common ASN.1 runtime
#include "asn_internal.h"         // internal stuff for decoding
#include "per_decoder.h"          // for uPER decoding

"""
include_set=set()
code_set=set()
for c in code:
    if c["type"]=="include" and c["name"] not in include_set:
        code_file+=f"#include \"{c['include']}\"\n"
        include_set.add(c["name"])

for c in code:
    if c["type"]=="code" and c["name"] not in code_set:
        code_file+=c["code"]+"\n"
        code_set.add(c["name"])
    



with open(f"./out/code_{name}.c","w") as f:
    f.write(code_file)

log_info(f"Code file: {code_file}")


import asn1tools
import json
from jinja2 import Environment,FileSystemLoader
import os


schema_name=name 
asn1_schema = asn1tools.compile_files(file_path,'uper')


with open(f"./json/{schema_name}.json", "r") as f:
    message = json.load(f)

with open(f"./out/code_{schema_name}.c","r") as f:
    code = f.read()
    # print(code)

encoded_message = asn1_schema.encode(schema_name, message)
print("hex encoded message: ", encoded_message.hex())
print(f"Encoded {schema_name} message: {encoded_message}")
c_array = ', '.join(str(b) for b in encoded_message)
print(f"Encoded {schema_name} message as C array: {{ {c_array} }}")


# Set up environment with directory of the template
env = Environment(loader=FileSystemLoader('.'))

# Load the template by filename
template = env.get_template('test.c.j2')

context={
    "schema_name": schema_name,
    "message": message,
    "encoded_message": encoded_message,
    "c_array": "{"+c_array+"}",
}

out=template.render(context)

with open(f"./test/test_{schema_name}.c", "w") as f:
    f.write(code+"\n\n"+out)
    print(f"test_{schema_name}.c generated successfully.")
    # print(out)