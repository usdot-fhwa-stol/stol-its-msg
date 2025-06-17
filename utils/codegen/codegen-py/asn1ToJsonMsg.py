def parseCli():
    """Parses script's CLI arguments.

    Returns:
        argparse.Namespace: arguments
    """
    parser = argparse.ArgumentParser(
        description="Converts ASN.1 message definitions to JSON format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("files", type=str, nargs="+", help="ASN.1 files")
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="output directory")
    parser.add_argument("-t", "--type", type=str, required=True, help="ASN.1 type")

    args = parser.parse_args()

    return args


def loadJinjaTemplate() -> jinja2.environment.Template:
    """Loads the jinja template for JSON message files.

    Returns:
        jinja2.environment.Template: jinja template
    """
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), trim_blocks=False)
    jinja_template = jinja_env.get_template("JsonMessageType.json.jinja2")

    return jinja_template


def asn1TypeToJson(type_name: str, asn1_type: Dict, asn1_types: Dict[str, Dict], asn1_values: Dict[str, Dict], asn1_sets: Dict[str, Dict], asn1_classes: Dict[str, Dict], asn1_raw: Dict[str, str], jinja_template: jinja2.environment.Template) -> str:
    """Converts parsed ASN.1 type information to a JSON file string.

    Args:
        type_name (str): type name
        asn1_type (Dict): type information
        asn1_types (Dict[str, Dict]): type information of all types by type
        asn1_values (Dict[str, Dict]): value information of all values by name
        asn1_sets (Dict[str, Dict]): set information of all sets by name
        asn1_classes (Dict[str, Dict]): class information of all classes by name
        asn1_raw (Dict[str, str]): raw string definition by type
        jinja_template (jinja2.environment.Template): jinja template

    Returns:
        str: JSON file string
    """
    jinja_context = asn1TypeToJinjaContext(type_name, asn1_type, asn1_types, asn1_values, asn1_sets, asn1_classes)
    if jinja_context is None:
        return None

    if type_name in asn1_raw:
        jinja_context["asn1_definition"] = asn1_raw[type_name].rstrip("\n")

    json_output = jinja_template.render(jinja_context)

    return json_output


def exportJson(json_output: str, type_name: str, output_dir: str):
    """Exports a JSON file.

    Exports to `output_dir`/`type_name`.json.

    Args:
        json_output (str): JSON file string
        type_name (str): type name / file name
        output_dir (str): output directory
    """
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.join(output_dir, f"{validJsonType(type_name)}.json")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json_output)


def main():
    args = parseCli()

    print("Parsing ASN.1 files ...")
    asn1_docs, asn1_raw = parseAsn1Files(args.files)
    asn1_types = extractAsn1TypesFromDocs(asn1_docs)
    asn1_values = extractAsn1ValuesFromDocs(asn1_docs)
    asn1_sets = extractAsn1SetsFromDocs(asn1_docs)
    asn1_classes = extractAsn1ClassesFromDocs(asn1_docs)

    checkTypeMembersInAsn1(asn1_types)

    jinja_template = loadJinjaTemplate()
    for type_name, asn1_type in asn1_types.items():
        json_output = asn1TypeToJson(type_name, asn1_type, asn1_types, asn1_values, asn1_sets, asn1_classes, asn1_raw, jinja_template)
        exportJson(json_output, type_name, args.output_dir)

    print(f"Generated JSON files for {len(asn1_types)} ASN.1 types.")


if __name__ == "__main__":
    main()