import os
import re


def find_duplicates(lines):
    token_set = set()
    duplicates=[]
    for line in lines:
        line = line.strip()
        if not line or line.startswith("--"):
            continue
        if "::=" in line:
            tokens = line.split("::=")
            token=tokens[0].strip()
            if token in token_set:
                duplicates.append(token)
                # print(f"Duplicate token found: {token} in file {file_path}")
            token_set.add(token)

    return duplicates

def combine_namespaces(spec_name,tmp_dir,out_dir):
    output_file = os.path.join(out_dir, f"{spec_name}.asn1")
    

    with open(output_file, 'w') as outfile:
        outfile.write(f"{spec_name.replace("_","-")} DEFINITIONS AUTOMATIC TAGS ::= BEGIN\n")
        for file in os.listdir(os.path.join(tmp_dir, spec_name)):
            if not file.endswith(".asn1"):
                continue
            file_path = os.path.join(tmp_dir, spec_name, file)
            with open(file_path, 'r') as infile:
                outfile.write(infile.read())
                outfile.write("\n")  # Add a newline between files

        outfile.write("END\n")
    print(f"Combined namespaces into {output_file}")


def process_file(file_path,out_dir,temp_dir):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    spec_name = os.path.basename(file_path)
    spec_name = spec_name.split(".")[0]

    namespace=None
    namespaces=set()

    for line in lines:
        if "::=" in line and "BEGIN" in line:
            namespace = line.split()[0].strip()
            namespaces.add(namespace)
    


    if len(namespaces) > 1:
        print(f"Multiple namespaces found: {namespaces}")
        duplicates = find_duplicates(lines)
        if not duplicates:
            print(f"No duplicate tokens found in {file_path}.")
            return
        print(f"Duplicate tokens found: {duplicates}")

        if not os.path.exists(os.path.join(temp_dir, spec_name)):
            os.makedirs(os.path.join(temp_dir, spec_name))

        separate_namespaces(file_path,spec_name,temp_dir)


        for file in os.listdir(os.path.join(temp_dir, spec_name)):

            if not file.endswith(".asn1"):
                continue

            namespace=file.split(".")[0]

            with open(os.path.join(temp_dir, spec_name,file), 'r') as f:
                tmp_lines= f.readlines()

            for idx in range(len(tmp_lines)):
                for duplicate in duplicates:
                    pattern=rf'\b{re.escape(duplicate)}\b'
                    new_word = f"{namespace}-{duplicate}"

                    tmp_lines[idx]=re.sub(pattern, new_word, tmp_lines[idx])

                for n in namespaces:
                    pattern_namespace = rf'{re.escape(n)}\.'
                    tmp_lines[idx] = re.sub(pattern_namespace, '', tmp_lines[idx])

            print(f"processing {namespace} with lenght {len(tmp_lines)}")
            with open(os.path.join(temp_dir,spec_name, f"{namespace}.asn1"), 'w') as f:
                f.writelines(tmp_lines)

        combine_namespaces(spec_name,temp_dir,out_dir)
        print(f"Processed {spec_name} with multiple namespaces.")
    else:
        print(f"Single namespace found in {file_path}. No processing needed.")
        with open(os.path.join(out_dir, f"{spec_name}.asn1"), 'w') as outfile:
            outfile.writelines(lines)

def separate_namespaces(file_path,spec_name,temp_dir):
    with open(file_path, 'r') as file:
        data = file.read()


    lines=data.splitlines()
    count=0
    lines_count=len(lines)
    namespaces=[]

    """
    Namespace parser
    """
    start=0
    end=0
    namespaces={}
    while count<lines_count:
        line=lines[count]
        if "::= BEGIN" in line:
            namespace=line.split()[0].strip()
            start=count
            
        if "END" in line:
            end=count
            end+=1
            namespaces[namespace]={
                "start":start,
                "end":end
            }
        
        count+=1

    """
        Write each namespace data to a file
    """
    # print(namespaces)
    for namespace in namespaces:
        with open(os.path.join(temp_dir, spec_name,f"{namespace}.asn1"), 'w') as file:
            for j in range(namespaces[namespace]["start"]+1, namespaces[namespace]["end"]-1):
                file.write(lines[j] + '\n')



def main():
    """Main function to process ASN.1 files."""

    temp_dir = "./asn1/tmp"
    out_dir = "./asn1/processed/"
    input_dir = "./asn1/raw/"

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    spec_files = os.listdir(input_dir)

    if len(spec_files) == 0:
        print("No ASN.1 files found in the input directory.")
        return

    for spec_file in spec_files:
        if not spec_file.endswith(".asn1"):
            continue

        name = spec_file.split(".")[0]

        print(f"Processing {name}...")

        process_file(os.path.join(input_dir, spec_file),out_dir,temp_dir)

if __name__ == "__main__":
    main()


