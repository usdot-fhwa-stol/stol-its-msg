import os
from asn1CodeGenerationUtils import *
from asn1ToConversionHeader import loadJinjaTemplates
import json
import logging
import argparse




class CodeGen:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing CodeGen")

        self.docs=None
        self.types=None
        self.values=None
        self.sets=None
        self.classes=None
        self.raw=None

        self.out_dir=None
        self.input_file_path=None
        self.templates=loadJinjaTemplates()
        self.name=None

        self.c_keywords = { "int", "float", "long","double", "char", "void", "if", "else", "while", "for", "return", "break", "continue", "switch", "case", "default", "struct", "union", "typedef", "static", "extern", "const", "volatile","class" }
        self.asn1_types=['SEQUENCE', 'SEQUENCE OF','CHOICE', 'ENUMERATED', 'OCTET STRING', 'BIT STRING', 'UTF8String', 'IA5String']
        self.asn1_primitives=['INTEGER', 'BOOLEAN']

        self.actual_types={}

    def validate_name(self, name):
        return name.replace(" ","_").replace("-","_")
    
    def process_bit_string(self, name, body):
        named_bits=body.get('named-bits', [])

        members=[]
        for bit in named_bits:
            if not bit:
                continue

            member_name=bit[0]
            member_value=bit[1]

            members.append({
                "name": self.validate_name(member_name),
                "value": member_value
            })

        return {
            "members": members,
            "struct_name": f"{self.validate_name(name)}_t",
            "function_name": self.validate_name(name),
            "includes": [{
                "name": f"{self.validate_name(name)}_converter.hpp"
            }]
        }

    def process_enumerated(self, name, body):
        values=body['values']
        members=[]

        for value in values:
            if not value:
                continue

            member_name=value[0]
            member_value=value[1]

            members.append({
                "name": self.validate_name(member_name),
                "value": member_value
            })

        includes=[{
            "name": f"{name}.h"
        }]

        return {
            "members": members,
            "struct_name": f"{self.validate_name(name)}_t",
            "function_name": self.validate_name(name),
            "includes": includes
        }
    
    def process_strings(self, name, body):
        return {
            "struct_name": f"{self.validate_name(name)}_t",
            "function_name": self.validate_name(name),
            "includes": [{
                "name": f"{self.validate_name(name)}_converter.hpp"
            }],
            "is_optional": body.get('optional', False)
        }


    def process_sequence(self,name,body):
        members=body['members']

        if "parameters" in body:
            parameters=body['parameters']
            if parameters[0]=="Set":
                return

        member_data=[]
        includes=[]
        for member in members:

            if not member:
                continue
            
            member_type=member['type']
            member_name=member['name']
            member_is_optional=member.get('optional', False)

            if "actual-parameters" in member:
                actual_type=member['actual-parameters'][0]['type']
                member_data.append({
                    "item_type": "complex",
                    "struct_name": f"{self.validate_name(actual_type)}_t",
                    "function_name": self.validate_name(actual_type),
                    "name": self.validate_name(member_name),
                    "is_optional": member_is_optional
                })

                includes.append({
                    "name": f"{self.validate_name(actual_type)}_converter.hpp"
                })
                continue

            if member_name in self.c_keywords:
                member_name=member_name.capitalize()

            if member_type in self.asn1_types:
                if member_type=="CHOICE":
                    choice_response=self.process_choice(name,member)
                    member_type=f"{name}__{member_name}"
                    self.logger.debug(f"sequence process_choice response: {json.dumps(choice_response, indent=4)}")
                    member_data.append({
                        "item_type": "choice",
                        "name": member_name,
                        "struct_name": f"{self.validate_name(member_type)}",
                        "function_name": self.validate_name(member_type),
                        "is_optional": member_is_optional,
                        "choices": choice_response["members"],
                    })

                    includes.extend(choice_response["includes"])

                elif member_type=="SEQUENCE":
                    seq_name=f"{self.validate_name(name)}__{member_name}"
                    seq_response=self.process_sequence(seq_name, member)
                    logging.debug(f"process_sequence response for name {name}: {json.dumps(seq_response, indent=4)}")
                    member_data.append({
                        "item_type": "sequence",
                        "name": member_name,
                        "struct_name": f"{self.validate_name(seq_name)}",
                        "function_name": self.validate_name(seq_name),
                        "is_optional": member_is_optional,
                        "members": seq_response['members'],
                    })

                    includes.extend(seq_response["includes"])

                elif member_type=="SEQUENCE OF":
                    seq_of_response=self.process_sequence_of(name,member)
                    member_type=f"{name}__{member_name}"
                    self.logger.debug(f"sequence process_sequence_of response: {json.dumps(seq_of_response, indent=4)}")
                    member_data.append({
                        "item_type": "sequence_of",
                        **seq_of_response,
                        "name": member_name,
                        "struct_name": f"{self.validate_name(member_type)}",
                        "function_name": self.validate_name(member_type),
                        "is_optional": member_is_optional,
                    })

                    includes.extend(seq_of_response["includes"])

            elif member_type in self.asn1_primitives:
                member_data.append({
                    "is_optional": member_is_optional,
                    "item_type": "simple",
                    "data_type": "bool" if member_type=="BOOLEAN" else "long",
                    "function_name": self.validate_name(member_type),
                    "struct_name": f"{self.validate_name(member_type)}_t",
                    "name": member_name
                })

                includes.append({
                    "name": f"{member_type}.h"
                })

            else:
                member_data.append({
                    "function_name": self.validate_name(member_type),
                    "struct_name": f"{self.validate_name(member_type)}_t",
                    "is_optional": member_is_optional,
                    "item_type": "complex",
                    "name": self.validate_name(member_name)
                })

                includes.append({
                    "name": f"{self.validate_name(member_type)}_converter.hpp"
                })

        includes_set=set(include["name"] for include in includes)
        includes=[{"name":name} for name in includes_set]

        return {
            "members": member_data,
            "includes": includes
        }
    
    def process_sequence_of(self,name,body):
        element=body['element']
        element_type=element['type']

        includes=[]

        is_sequence_function_present=False

        response_seq_of={
            "struct_name": f"{self.validate_name(name)}_t",
            "function_name": self.validate_name(name),
            "sequence_function_present": is_sequence_function_present,
        }

        actual_type=None
        if "actual-parameters" in element:
            actual_parameters=element['actual-parameters']
            actual_type=actual_parameters[0]['type']

            includes.append({
                "name": f"{element_type}.h"
            })

            includes.append({
                "name": f"{self.validate_name(actual_type)}_converter.hpp"
            })

            return{
                "actual_type": actual_type,
                "element_struct_name": f"{self.validate_name(actual_type)}_t",
                "element_function_name": self.validate_name(actual_type),
                "includes": includes
            }
        
        if element_type in self.asn1_types:
            if element_type=="SEQUENCE":
                seq_name=f"{self.validate_name(name)}__Member"
                is_sequence_function_present=True
                response=self.process_sequence(seq_name, element)
                logging.debug(f"process_sequence response for name {name}: {json.dumps(response, indent=4)}")
                response_seq_of['seq']={
                    "function_name": self.validate_name(seq_name),
                    "struct_name": f"{self.validate_name(seq_name)}",
                    "members": response['members'],
                }
                response_seq_of['element_struct_name']=f"{self.validate_name(seq_name)}"
                response_seq_of['element_function_name']=self.validate_name(seq_name)
                response_seq_of['sequence_function_present']=is_sequence_function_present

                includes.extend(response['includes'])
            elif element_type=="CHOICE":
                pass
        else:
            response_seq_of['element_struct_name']=f"{self.validate_name(element_type)}_t"
            response_seq_of['element_function_name']=self.validate_name(element_type)

            includes.append({
                "name": f"{self.validate_name(element_type)}_converter.hpp"
            })

            includes.append({
                "name": f"{self.validate_name(element_type)}.h"
            })


        return {
            **response_seq_of,
            "includes": includes,
        }
                
    
    def process_choice(self,name,body):
        members=body['members']

        choices=[]
        includes=[]

        for member in members:
            if not member:
                continue

            member_type=member['type']
            member_name=member['name']

            if "actual-parameters" in member:
                actual_type=member['actual-parameters'][0]['type']
                
                choices.append({
                    "name": self.validate_name(member_name),
                    "item_type":"complex",
                    "struct_name": f"{self.validate_name(actual_type)}_t",
                    "function_name": self.validate_name(actual_type),
                })

                includes.append({
                    "name": f"{self.validate_name(actual_type)}_converter.hpp"
                })

                continue

            if member_name in self.c_keywords:
                member_name=member_name.capitalize()

            if member_type in self.asn1_types:
                if member_type=="SEQUENCE OF":
                    seq_of_response=self.process_sequence_of(name,member)
                    self.logger.debug(f"process_choice sequence_of response: {json.dumps(seq_of_response, indent=4)}")
                    choices.append({
                        "name": self.validate_name(member_name),
                        "item_type": "sequence_of",
                        **seq_of_response,
                        "struct_name": f"{self.validate_name(member_type)}",
                        "function_name": self.validate_name(member_type),
                    })

                    includes.extend(seq_of_response["includes"])
                
            else:
                choices.append({
                    "function_name": self.validate_name(member_type),
                    "struct_name": f"{self.validate_name(member_type)}_t",
                    "name": self.validate_name(member_name),
                    "item_type": "complex",
                })

                includes.append({
                    "name": f"{self.validate_name(member_type)}_converter.hpp"
                })

        includes_set=set(include["name"] for include in includes)
        includes=[{"name":name} for name in includes_set]
        return {
            "members": choices,
            "includes": includes
        }

    def process_class(self,key,body):
        members=body['members']
        class_members=body['class_members']

        for class_member in class_members:
            new_type={
                "type":"SEQUENCE",
                "members":[
                    {
                        "type":members[0]['type'],
                        "name":self.validate_name(members[0]['name']),
                    },
                    {
                        **class_members[class_member],
                        "name":self.validate_name(members[1]['name'])
                    }
                ]
            }
            self.logger.debug(f"Processing class member {class_member}")
            response=self.process_sequence(class_member,new_type)
            response['includes'].append({
                "name": f"{key}.h"
            })
            self.render_sequence(class_member,response,key)
            self.logger.debug(f"class type {key} process_sequence response: {json.dumps(response, indent=4)}")

    def process_comments(self,name):
        comments=None
        if name in self.raw:
            comments=self.raw[name]
        else:
            return []
        
        additional_comments=[
            "This file contains automatically generated C++ encoding and decoding functions using ASN.1 definitions and Jinja2 templates.",
            "Do not edit this file manually. If you need to make changes, modify the ASN"
            "Below is the schema used to generate the functions:\n\n"
        ]

        c_s=[]
        if comments:
            c_s=comments.split("\n")
            c_s=[c for c in c_s]
        c_s=[*additional_comments, *c_s]
        comments="\n".join(c_s)

        return c_s

    def process_types(self):

        for key,value in list(self.types.items()):
            d_type=value['type']

            logging.info(f"Processing type {key} with type {d_type}")

            if d_type=="SEQUENCE":
                response=self.process_sequence(key,value)
                response['includes'].append({
                    "name": f"{self.validate_name(key)}_converter.hpp"
                })
                logging.info(f"Rendering sequence {key}")
                self.render_sequence(key,response)
                
            elif d_type=="SEQUENCE OF":
                response=self.process_sequence_of(key,value)
                logging.info(f"Rendering SEQUENCE OF {key}")
                self.render_sequence_of(key,response)

            elif d_type=="ENUMERATED":
                response=self.process_enumerated(key,value)
                response['includes'].append({
                    "name": f"{self.validate_name(key)}_converter.hpp"
                })
                logging.info(f"Rendering ENUMERATED {key}")
                self.render_enumerated(key,response)

            elif d_type=="OCTET STRING" or d_type=="IA5String":
                response=self.process_strings(key,value)
                logging.debug(f"process_strings response for {key}: {json.dumps(response, indent=4)}")
                response['includes'].append({
                    "name": f"{self.validate_name(key)}_converter.hpp"
                })
                if d_type=="OCTET STRING":
                    logging.info(f"Rendering OCTET STRING {key}")
                    self.render_octet_string(key,response)
                elif d_type=="IA5String":
                    logging.info(f"Rendering IA5String {key}")
                    self.render_ia5string(key,response)
    
            elif d_type=="CHOICE":
                response=self.process_choice(key,value)
                logging.debug(f"process_choice response for {key}: {json.dumps(response, indent=4)}")
                response['includes'].append({
                    "name": f"{self.validate_name(key)}_converter.hpp"
                })
                logging.info(f"Rendering CHOICE {key}")
                self.render_choice(key,response)

            elif d_type=="BIT STRING":
                response=self.process_bit_string(key,value)
                response['includes'].append({
                    "name": f"{self.validate_name(key)}_converter.hpp"
                })
                logging.info(f"Rendering BIT STRING {key}")
                self.render_bit_string(key,response)
                
                
            elif d_type in self.asn1_primitives:
                logging.info(f"Rendering primitive {key} with type {d_type}")
                self.render_primitive(key,value)

            else:
                if d_type!="CLASS":
                    self.render_primitive(key, value)


    def render_bit_string(self,name,data):
        comments=self.process_comments(name)
        data['includes'].append({
            "name": f"{name}.h"
        })

        rendered_template=self.templates["BIT_STRING"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            members=data['members'],
            includes=data['includes'],
            comments=comments
        )

        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.cpp"), "w") as f:
            f.write(rendered_template)

        rendered_template=self.templates["HEADER"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            include_name=f"{name}.h"
        )
        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.hpp"), "w") as f:
            f.write(rendered_template)

    def render_octet_string(self,name,data):
        comments=self.process_comments(name)
        data['includes'].append({
            "name": f"{name}.h"
        })

        rendered_template=self.templates["OCTET_STRING"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            includes=data['includes'],
            comments=comments,
            is_optional=data.get('is_optional', False)
        )

        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.cpp"), "w") as f:
            f.write(rendered_template)

        rendered_template=self.templates["HEADER"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            include_name=f"{name}.h"
        )
        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.hpp"), "w") as f:
            f.write(rendered_template)

    def render_ia5string(self,name,data):
        comments=self.process_comments(name)
        data['includes'].append({
            "name": f"{name}.h"
        })

        rendered_template=self.templates["IA5STRING"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            includes=data['includes'],
            comments=comments,
            is_optional=data.get('is_optional', False)
        )

        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.cpp"), "w") as f:
            f.write(rendered_template)

        rendered_template=self.templates["HEADER"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            include_name=f"{name}.h"
        )
        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.hpp"), "w") as f:
            f.write(rendered_template)

    def render_choice(self,name,data):
        comments=self.process_comments(name)
        
        data['includes'].append({
            "name": f"{name}.h"
        })

        rendered_template=self.templates["CHOICE"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            choices=data['members'],
            includes=data['includes'],
            comments=comments
        )

        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.cpp"), "w") as f:
            f.write(rendered_template)

        rendered_template=self.templates["HEADER"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            include_name=f"{name}.h"
        )
        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.hpp"), "w") as f:
            f.write(rendered_template)

    def render_enumerated(self,name,data):
        comments=self.process_comments(name)
        

        rendered_template=self.templates["ENUMERATED"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            members=data['members'],
            includes=data.get('includes', []),
            comments=comments
        )

        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.cpp"), "w") as f:
            f.write(rendered_template)

        rendered_template=self.templates["HEADER"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            include_name=f"{name}.h"
        )
        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.hpp"), "w") as f:
            f.write(rendered_template)

    def render_primitive(self,name,data):
        comments=self.process_comments(name)
        includes=[]
        includes.append({
            "name": f"{name}.h"
        })

        rendered_template=self.templates["PRIMITIVES"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            data_type=data['type'],
            includes=includes,
            comments=comments
        )

        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.cpp"), "w") as f:
            f.write(rendered_template)

        rendered_template=self.templates["HEADER"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            include_name=f"{name}.h"
        )
        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.hpp"), "w") as f:
            f.write(rendered_template)




    def render_sequence(self,name,data,h_name=None):
        comments=self.process_comments(name)
        logging.debug(f"Rendering sequence {name} with data: {json.dumps(data, indent=4)}")
        rendered_template=self.templates["SEQUENCE"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            members=data['members'],
            includes=data['includes'],
            comments=comments
        )

        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.cpp"), "w") as f:
            f.write(rendered_template)


        rendered_template=self.templates["HEADER"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            include_name=f"{h_name}.h" if h_name else f"{name}.h"
        )

        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.hpp"), "w") as f:
            f.write(rendered_template)

    def render_sequence_of(self,name,data):
        comments=self.process_comments(name)
        data['includes'].append({
            "name":f"{name}.h"
        })
        logging.debug(f"Rendering sequence_of {name} with data: {json.dumps(data, indent=4)}")
        rendered_template=self.templates["SEQUENCE_OF"].render(
            **data,
            comments=comments
        )

        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.cpp"), "w") as f:
            f.write(rendered_template)


        rendered_template=self.templates["HEADER"].render(
            function_name=self.validate_name(name),
            struct_name=f"{self.validate_name(name)}_t",
            include_name=f"{name}.h"
        )

        with open(os.path.join(self.out_dir, f"{self.validate_name(name)}_converter.hpp"), "w") as f:
            f.write(rendered_template)

    def initialize(self):
        files=[self.input_file_path]

        asn1_docs,asn1_raw=parseAsn1Files(files)
        self.docs=asn1_docs
        self.raw=asn1_raw

        self.types=extractAsn1TypesFromDocs(asn1_docs)
        self.values=extractAsn1ValuesFromDocs(asn1_docs)
        self.sets=extractAsn1SetsFromDocs(asn1_docs)
        self.classes=extractAsn1ClassesFromDocs(asn1_docs)

        

        updated_classes={}
        for class_name, class_body in self.classes.items():
            members=class_body['members']

            for member in members:
                if not member:
                    continue

                member_type=member['type']
                member_name=member['name']

                if not member_name or not member_type:
                    continue

                updated_classes[f"{class_name}.{member_name}"] = member_type

        self.classes=updated_classes


        # look for set in spec files and replace its content with the actual type
        for key, value in list(self.types.items()):
            if "parameters" in value:
                parameters = value['parameters']
                if parameters[0] == "Set":
                    self.types[key]['type']="CLASS"

            class_type=None
            if "members" in value:
                members = value['members']
                for member in members:
                    if not member:
                        continue

                    member_type = member['type']
                    class_type=member['type'].split(".")[0]
                    if member_type in self.classes:
                        member['type'] = self.classes[member_type]

            new_types={}
            for set_key, set_value in self.sets.items():
                set_class=set_value['class']
                members=set_value['members']
               
                if set_class==class_type:
                    new_types[set_key]={
                        "type":"CHOICE",
                        "members":[]
                    }
                    for member in members:
                        if not member:
                            continue

                        member_type = member['type']
                        new_types[set_key]['members'].append({
                            "type":member_type,
                            "name": member_type
                        })

            if new_types:
                self.types[key]["class_members"]=new_types


        for key, value in self.types.items():
            if self.types[key]["type"]=="SEQUENCE":
                members=value['members']

                for member in members:
                    if not member:
                        continue

                    member_type=member['type']
                    if member_type=="OpenType":
                        content=member['table'][0]

                        if value["class_members"][content]:
                            member['type']=value["class_members"][content]['type']
                            member['members']=value["class_members"][content]['members']

        logging.info(f"processing types for {self.name} with {len(self.types)} types")
        self.process_types()
        logging.debug(f"Processed types: {json.dumps(self.types, indent=4)}")

        logging.info(f"processing classes for {self.name} with {len(self.classes)} classes")
        for key,value in list(self.types.items()):
            d_type=value['type']

            logging.info(f"Processing type {key} with type {d_type}")

            if d_type=="CLASS":
                self.process_class(key,value)


def parseCli():
    """Parses script's CLI arguments.

    Returns:
        argparse.Namespace: arguments
    """

    parser = argparse.ArgumentParser(
        description="Generates C++ encoding and decoding functions from ASN.1 definitions.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument("files", type=str, nargs="+", help="ASN1 files directory")
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="output package directory")
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level"
    )

    args = parser.parse_args()

    return args

def main():

    args=parseCli()

    logging.basicConfig(
        level=args.log_level,  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),                    # Console
            logging.FileHandler("CodeGen.log","w")   # File
        ]
    )

    output_dir=args.output_dir

    input_dir=args.files[0]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    

    spec_files=os.listdir(input_dir)

    for spec_file in spec_files:
        if not spec_file.endswith(".asn1"):
            continue

        name=spec_file.split(".")[0]

        if not os.path.exists(os.path.join(output_dir, name)):
            os.makedirs(os.path.join(output_dir, name))

        file_path=os.path.join(input_dir, spec_file)
        final_output_dir=os.path.join(output_dir, name)

        codegen=CodeGen()
        codegen.name=name
        codegen.out_dir=final_output_dir
        codegen.input_file_path=file_path
        codegen.initialize()

if __name__ =="__main__":
    main()


