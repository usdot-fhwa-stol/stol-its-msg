import unittest
from src.asn1ToJsonMsg import asn1TypeToJsonMsg
from src.utils.asn1CodeGenerationUtils import parseAsn1Files

class TestASN1ToJsonMsg(unittest.TestCase):

    def setUp(self):
        self.asn1_files = ["path/to/test_file.asn1"]
        self.asn1_docs, self.asn1_raw = parseAsn1Files(self.asn1_files)

    def test_conversion(self):
        for type_name, asn1_type in self.asn1_docs.items():
            json_output = asn1TypeToJsonMsg(type_name, asn1_type)
            self.assertIsNotNone(json_output)
            self.assertIsInstance(json_output, dict)

    def test_json_structure(self):
        # Example test to check the structure of the generated JSON
        type_name = "ExampleType"
        asn1_type = self.asn1_docs[type_name]
        json_output = asn1TypeToJsonMsg(type_name, asn1_type)
        
        # Check for expected keys in the JSON output
        self.assertIn("key1", json_output)
        self.assertIn("key2", json_output)
        self.assertIsInstance(json_output["key1"], list)

if __name__ == "__main__":
    unittest.main()