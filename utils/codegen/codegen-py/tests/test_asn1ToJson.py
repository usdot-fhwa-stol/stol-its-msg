import subprocess
import os
import tempfile
import asn1tools
import argparse
import jinja2
from test_msgs import *
import sys
import shutil


def parseCli():
    """Parses script's CLI arguments.

    Returns:
        argparse.Namespace: arguments
    """

    parser = argparse.ArgumentParser(
        description="Test script for ASN.1 to JSON conversion using asn1tools.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-di", "--docker-image", type=str, default="ghcr.io/ika-rwth-aachen/etsi_its_messages:asn1c", help="asn1c Docker image")

    args = parser.parse_args()

    return args

def load_jinja_templates():
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), trim_blocks=False)
    jinja_templates = {}
    jinja_templates["TEST"]= jinja_env.get_template("TEST.c.j2")

    return  jinja_templates


def main():

    args = parseCli()

    templates=load_jinja_templates()

    raw_files=os.listdir("./asn1/raw/carma_j2735")

    file_names= [file.split(".")[0] for file in raw_files if file.endswith('.asn')]

    if not os.path.exists("./etsi_its_testing"):
        os.makedirs("./etsi_its_testing")
    else:
        #  Clean up existing files
        for file in os.listdir("./etsi_its_testing"):
            file_path = os.path.join("./etsi_its_testing", file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
            

    for name in file_names:
        print(f"Processing ASN.1 file: {name}")
        asn1_file_path = f"./asn1/raw/carma_j2735/{name}.asn"
        code_file_path=f"./etsi_its_conversion/{name}.c"

        if not os.path.exists(asn1_file_path):
            print(f"Warning: ASN.1 file {asn1_file_path} does not exist. Skipping conversion.")
            sys.exit(0)
        with open(asn1_file_path, 'r') as f:
            asn1_content = f.read()

        if not os.path.exists(code_file_path):
            print(f"Warning: Code file {code_file_path} does not exist. Skipping conversion.")
            sys.exit(0)
        with open(code_file_path, 'r') as f:
            code_content = f.read()


        if name not in messages_dict:
            print(f"Warning: No message definition found for {name}. Skipping conversion.")
            sys.exit(0)

        msgs=messages_dict[name]

        # Load ASN.1 definitions
        spec = asn1tools.compile_files(asn1_file_path, 'uper')

        msg_count=1
        for msg in msgs:
            
            encoded_message = spec.encode(f"{name}", msg)
            c_array = ', '.join(str(b) for b in encoded_message)
            print(f"Encoded message for {name}: {c_array}") 

            context={
                "schema_name": name,
                "message": msg,
                "encoded_message": encoded_message,
                "c_array": "{"+c_array+"}",
            }

            test_code= templates["TEST"].render(context)

            with open(f"./etsi_its_testing/TEST_{msg_count}_{name}.c", "w") as f:
                f.write(code_content+"\n\n"+test_code)

            msg_count += 1

    # with tempfile.TemporaryDirectory() as temp_input_dir:
    #     with tempfile.TemporaryDirectory() as temp_output_dir:
    #         # Define the command to run the ASN.1 to JSON conversion
    #         if args.temp_dir is None:
    #             container_input_dir = temp_input_dir
    #             container_output_dir = temp_output_dir
    #             test_cmd_file = tempfile.NamedTemporaryFile(delete=False).name
            
    #         with open(test_cmd_file, "w") as f:
    #             f.write("#!/bin/bash\n")
                


    #         subprocess.run(["docker", "run", "--rm", "-u", f"{os.getuid()}:{os.getgid()}", "-v", f"{container_input_dir}:/input:ro", "-v", f"{container_output_dir}:/output", "-v", f"{test_cmd_file}:/asn1c.sh", args.docker_image], check=True)


if __name__ == "__main__":
    main()