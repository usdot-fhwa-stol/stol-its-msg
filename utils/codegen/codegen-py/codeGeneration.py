from asn1CodeGenerationUtils import *
from jinja2 import Environment, FileSystemLoader
from asn1ToConversionHeader import loadJinjaTemplates
import json
import os

primitive_types=["INTEGER","BIT STRING","OCTET STRING","ENUMERATED","BOOLEAN"]
complex_types=["SEQUENCE","SEQUENCE OF","CHOICE","IA5String"]
c_keywords=["int","char","float","double","long","short","void","unsigned","signed","const","volatile","static","extern","register","inline"]



templates= loadJinjaTemplates()
tag="carma_j2735_"

def int_type(min_val,max_val):
    
    if min_val is None or max_val is None:
        print(f"Error: min_val or max_val is None for int_type: {min_val}, {max_val}")
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
        

def process_primitive(asn1_name,asn1_info,code):
    print(f"Processing primitive: {asn1_name} {asn1_info['type']}")
    if asn1_info["type"] == "INTEGER":
        if "restricted-to" in asn1_info:
            min_val=asn1_info["restricted-to"][0][0]
            max_val=asn1_info["restricted-to"][0][1]
            print(f"INTEGER: {asn1_name} min: {min_val} max: {max_val}")

        else:
            print(f"Error: {asn1_name} is an INTEGER but has no restricted-to")

        context={
            "type":"simple",
            "asn1_type":int_type(min_val,max_val),
            "struct_name":asn1_name,
            # "data_type":"(double)",
            "function_name":"cJSON_AddNumberToObject"
        }
        print(f"INTEGER: {asn1_name} context: {context}")
        
        return context

    elif asn1_info["type"] == "BIT STRING":
        size=asn1_info["size"][0] if "size" in asn1_info else 0
        named_bits=asn1_info["named-bits"] if "named-bits" in asn1_info else []
        print(f"BIT STRING: {asn1_name} size: {size} named-bits: {named_bits}")
        
        members=[]
        for named_bit in named_bits:
            if not named_bit:
                print(f"Error: {asn1_name} has a None named bit")
                continue
            
            bit_name=named_bit[0]
            bit_index=named_bit[1]

            members.append({
                "name":validate_name(bit_name),
                "index":bit_index,
            })
            

        context={
            "struct_name":tag+asn1_name,
            "members":members,
        }

        print(f"BIT STRING: {asn1_name} context: {context}")

        render_def=templates["BIT STRING"].render(context)

        code.append({
            "type":"code",
            "name":tag+asn1_name,
            "code":render_def
        })

        code.append({
            "type":"include",
            "name":tag+asn1_name,
            "include":f"{tag}{asn1_name}.h"
        })

        return {
            "type":"complex",
            "struct_name":validate_name(asn1_info['type']),
            "asn1_type":tag+asn1_name.capitalize(),
            "function_name":"cJSON_AddItemToObject"
        }

    elif asn1_info["type"] == "ENUMERATED":
        vals=asn1_info["values"] if "values" in asn1_info else []

        members=[]
        for val in vals:
            if not val:
                print(f"Error: {asn1_name} has a None value")
                continue

            val_name=val[0]
            val_value=val[1]

            members.append({
                "name":val_name,
                "index":val_value,
            })

        context={
            "struct_name":tag+asn1_name,
            "members":members,
        }
        print(f"ENUMERATED: {asn1_name} members context: {context}")
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
            "struct_name":tag+validate_name(asn1_name),
            "function_name":"cJSON_AddItemToObject"
        }

        print(f"ENUMERATED: {asn1_name} res: {res}")

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
            print(f"Error: {asn1_name} is an OCTET STRING but has an invalid size: {size_len}")


        rendered=templates["OCTET STRING"].render({
            "struct_name":tag+asn1_name,
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
            "struct_name":tag+validate_name(asn1_name),
            "function_name":"cJSON_AddItemToObject"
        }
        print(f"OCTET STRING: {asn1_name} res: {res}")
        return res

    elif asn1_info["type"] == "BOOLEAN":
        res={
            "type":"simple",
            "asn1_type":"bool",
            "struct_name":tag+validate_name(asn1_name),
            # "data_type":"(cJSON_bool)",
            "function_name":"cJSON_AddBoolToObject"
        }

        print(f"BOOLEAN: {asn1_name} res: {res}")

        return res
    
    
    
    else:
        print(f"Error: {asn1_name} is an unknown type: {asn1_info['type']}")



def process_complex(asn1_name,asn1_info,asn1_types,asn1_values,asn1_classes,code):
    print(f"Processing complex: {asn1_name} {asn1_info['type']}")
    if asn1_info['type']=="SEQUENCE":
        out=[]
        for member in asn1_info["members"]:
            if not member:
                print(f"Error: {asn1_name} has a None member")
                continue

            member_type=member["type"]
            member_name=member["name"]

            if member_name in c_keywords:
                member_name=member_name[0].upper()+member_name[1:]

            member_optional=member["optional"] if "optional" in member else False
            print(f"Member: {member_name} Type: {member_type} Optional: {member_optional}")

            if member_type in asn1_classes:
                print(f"Member: {member_name} Type: {member_type} is a class")
                member_type=asn1_classes[member_type]


            if member_type in primitive_types:
                print(f"Member: {member_name} Type: {member_type} is a primitive")
                res=process_primitive(member_name,member,code)
                print(f"Member: {member_name} Type: {member_type} res: {res}")

            elif member_type in complex_types:
                print(f"Member: {member_name} Type: {member_type} is a complex")
                res=process_complex(member_name,member,asn1_types,asn1_values,asn1_classes,code)
                print(f"Member: {member_name} Type: {member_type} res: {res}")
            else:
                print(f"Member: {member_name} Type: {member_type} is one of type")
                res=rec(member_type,asn1_types[member_type],asn1_types,asn1_values,asn1_classes,code)
                print(f"Member: {member_name} Type: {member_type} res: {res}")

            if res:
                if member_optional:
                    res["is_optional"]=True
                else:
                    res["is_optional"]=False

                res['struct_type']=member_type
                res['name']=member_name
                out.append(res)
        

        context={
            "struct_name":tag+validate_name(asn1_name),
            "asn1_type":asn1_name.capitalize(),
            "members":out,
        }

        print(f"SEQUENCE: {asn1_name} context: {context}")

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
            "struct_name":tag+validate_name(asn1_name),
            "asn1_type":asn1_info,
            "function_name":"cJSON_AddItemToObject",
        }
        print(f"SEQUENCE: {asn1_name} res: {res}")

        return res

    elif asn1_info['type']=="SEQUENCE OF":
        print(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}")
        element=asn1_info["element"]
        size=asn1_info["size"]
        min_size=size[0][0]
        max_size=size[0][1]
        print(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element} min_size: {min_size} max_size: {max_size}")

        if "name" in asn1_info:
            name=asn1_info["name"]
            print(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: name {name}")

        if "optional" in asn1_info:
            optional=asn1_info["optional"]
            

        if element['type'] in primitive_types:
            print(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} is a primitive")
            res=process_primitive(name,element)
            print(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} res: {res}")

        if element['type'] in complex_types:
            print(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} is a complex")
            res=process_complex("",element,asn1_types,asn1_values,asn1_classes,code)
            print(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} res: {res}")
        
        if element['type'] in asn1_types:
            print(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} is one of type")
            res=rec(asn1_name,asn1_types[element["type"]],asn1_types,asn1_values,asn1_classes,code)
            print(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} res: {res}")

        print(f"SEQUENCE OF: {asn1_name} {asn1_info['type']}: element {element['type']} res: {res}")


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
        # print(f"SEQUENCE OF: {asn1_name} {asn1_info['type']} res :  {res}")



        return {
            "type":"complex",
            "struct_name":tag+validate_name(asn1_name),
            "asn1_type":asn1_info,
            "function_name":"cJSON_AddItemToObject",
            "element_type":res["struct_name"],
            "min_size":min_size,
            "max_size":max_size,
            "is_optional":optional if "optional" in asn1_info else False
        }
        

    elif asn1_info["type"] == "IA5String":
        

        context={
            "struct_name":tag+validate_name(asn1_name),
            "asn1_type":asn1_name,
            "function_name":"cJSON_AddItemToObject",
        }

        rendered=templates["IA5STRING"].render(context)

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
            "struct_name":tag+validate_name(asn1_name),
            "function_name":"cJSON_AddItemToObject"
        }

        print(f"IA5String: {asn1_name} res: {res}")

        return res

    elif asn1_info["type"] == "CHOICE":
        print(f"CHOICE: {asn1_name} {asn1_info['type']}")
        out=[]
        for member in asn1_info["members"]:
            if not member:
                print(f"Error: {asn1_name} has a None member")
                continue

            member_type=member["type"]
            member_name=member["name"]

            if member_name in c_keywords:
                member_name=member_name[0].upper()+member_name[1:]

            print(f"Member: {member_name} Type: {member_type}")

            if member_type in asn1_classes:
                print(f"Member: {member_name} Type: {member_type} is a class")
                member_type=asn1_classes[member_type]


            if member_type in primitive_types:
                print(f"Member: {member_name} Type: {member_type} is a primitive")
                res=process_primitive(member_name,member,code)
                print(f"Member: {member_name} Type: {member_type} res: {res}")

            elif member_type in complex_types:
                print(f"Member: {member_name} Type: {member_type} is a complex")
                res=process_complex(member_name,member,asn1_types,asn1_values,asn1_classes,code)
                print(f"Member: {member_name} Type: {member_type} res: {res}")
            else:
                print(f"Member: {member_name} Type: {member_type} is one of type")
                res=rec(member_type,asn1_types[member_type],asn1_types,asn1_values,asn1_classes,code)
                print(f"Member: {member_name} Type: {member_type} res: {res}")

            if res:
                res['struct_type']=member_type
                res['name']=member_name
                out.append(res)
        

        context={
            "struct_name":tag+asn1_name,
            "asn1_type":asn1_name.capitalize(),
            "members":out,
        }

        print(f"CHOICE: {asn1_name} context: {context}")

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
            "struct_name":tag+validate_name(asn1_name),
            "asn1_type":asn1_info,
            "function_name":"cJSON_AddItemToObject",
        }
        print(f"CHOICE: {asn1_name} res: {res}")
        return res


def rec(asn1_name,asn1_info,asn1_types,asn1_values,asn1_classes,code):
    print(f"Recursing: {asn1_name} {asn1_info['type']}")
    if asn1_info["type"] in primitive_types:
        print(f"Primitive: {asn1_name} {asn1_info['type']}")
        return process_primitive(asn1_name,asn1_info,code)
        
    if asn1_info["type"] in complex_types:
        print(f"Complex: {asn1_name} {asn1_info['type']}")
        return process_complex(asn1_name,asn1_info,asn1_types,asn1_values,asn1_classes,code)


    if asn1_info['type'] in asn1_types:
        print(f"ASN1: {asn1_name} {asn1_info['type']}")
        obj=asn1_types[asn1_info['type']]
        struct_type=asn1_info['type']
        res=rec(asn1_name,obj,asn1_types,asn1_values,asn1_classes,code)
        if res:
            res['struct_type']=struct_type
        print(f"ASN1: {asn1_name} {asn1_info['type']} res: {res}")
        return res
    
    if asn1_info['type'] in asn1_classes:
        print(f"ASN1 CLASS: {asn1_name} {asn1_info['type']}")
        obj_type=asn1_classes[asn1_info['type']]
        res=rec(asn1_name,asn1_types[obj_type],asn1_types,asn1_values,asn1_classes,code)
        print(f"ASN1 CLASS: {asn1_name} {asn1_info['type']} res: {res}")
        return res

def generate_code(file_path):
    files=[file_path]
    name=os.path.basename(file_path).split("/")[-1].split(".")[0]
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
                print(f"Error: {asn1_class} has a None member")
                continue

            member_type=member["type"]
            member_name=member["name"]
            print(f"Member: {member_name} Type: {member_type}")


            if not member_type or not member_name:
                print(f"Error: {asn1_class} has a None member type or name")
                continue

            new_classes[f"{asn1_class}.{member_name}"]=member_type
        
    asn1_classes=new_classes

    code=[]
    res=rec(list(asn1_types.keys())[0],asn1_types[list(asn1_types.keys())[0]],asn1_types,asn1_values,asn1_classes,code)


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
            code_file+=f"#include \"../etsi_its_coding/{tag}{c['include']}\"\n"
            include_set.add(c["name"])

    for c in code:
        if c["type"]=="code" and c["name"] not in code_set:
            code_file+=c["code"]+"\n"
            code_set.add(c["name"])
    

    with open(f"./etsi_its_conversion/{name}.c", "w") as f:
        f.write(code_file)


def main():

    #  make sure the etsi_its_conversion directory exists
    if not os.path.exists("./etsi_its_conversion"):
        os.makedirs("./etsi_its_conversion")

    else:
        # empty the directory
        for file in os.listdir("./etsi_its_conversion"):
            file_path = os.path.join("./etsi_its_conversion", file)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)

    


    spec_files=os.listdir("./asn1/raw/carma_j2735")

    for spec_file in spec_files:
        if not spec_file.endswith(".asn"):
            continue

        print(f"Processing {spec_file} ...")
        file_path=os.path.join("./asn1/raw/carma_j2735",spec_file)
        generate_code(file_path)


    

if __name__ == "__main__":
    main()