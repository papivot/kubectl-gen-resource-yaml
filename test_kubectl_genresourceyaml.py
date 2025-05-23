import unittest
import io
import sys
from unittest.mock import patch

# Assuming kubectl-genresourceyaml.py is in the same directory or accessible in PYTHONPATH
from kubectl_genresourceyaml import traverse_spec_objects

class TestTraverseSpecObjects(unittest.TestCase):

    def run_test_with_schema(self, schema, expected_output):
        """Helper function to run traverse_spec_objects and compare output."""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        traverse_spec_objects(schema, 1)  # Initial indentation level of 1
        sys.stdout = sys.__stdout__  # Reset stdout
        self.assertEqual(captured_output.getvalue().strip(), expected_output.strip())

    def test_various_data_types_and_structures(self):
        sample_schema = {
            "stringField": {"type": "string"},
            "stringFieldWithDefault": {"type": "string", "default": "hello"},
            "integerField": {"type": "integer"},
            "integerFieldWithDefault": {"type": "integer", "default": 123},
            "booleanField": {"type": "boolean"},
            "booleanFieldWithDefault": {"type": "boolean", "default": True},
            "numberField": {"type": "number"},
            "numberFieldWithDefault": {"type": "number", "default": 3.14},
            "noTypeField": {},
            "arrayOfString": {
                "type": "array",
                "items": {"type": "string"}
            },
            "arrayOfStringWithDefault": {
                "type": "array",
                "items": {"type": "string"},
                "default": ["a", "b"]
            },
            "arrayOfObjects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nestedString": {"type": "string"},
                        "nestedIntWithDefault": {"type": "integer", "default": 42}
                    }
                }
            },
            "nestedObject": {
                "type": "object",
                "properties": {
                    "childString": {"type": "string"},
                    "childObject": {
                        "type": "object",
                        "properties": {
                            "grandchildBoolean": {"type": "boolean", "default": False}
                        }
                    }
                }
            },
            "arrayWithNoItemType": { # Test case for array with no item type
                "type": "array",
                "items": {}
            },
            "objectWithNoProperties":{ # Test case for object with no properties
                "type": "object"
            }
        }

        expected_output = """
 stringField: <string>
 stringFieldWithDefault: <string> # Default: hello
 integerField: <integer>
 integerFieldWithDefault: <integer> # Default: 123
 booleanField: <boolean>
 booleanFieldWithDefault: <boolean> # Default: True
 numberField: <number>
 numberFieldWithDefault: <number> # Default: 3.14
 noTypeField: <no_type_specified>
 arrayOfString: 
  - <string>
 arrayOfStringWithDefault: 
  - <string> # Default: ['a', 'b']
 arrayOfObjects:
  - 
   nestedString: <string>
   nestedIntWithDefault: <integer> # Default: 42
 nestedObject:
  childString: <string>
  childObject:
   grandchildBoolean: <boolean> # Default: False
 arrayWithNoItemType: 
  - <no_type_specified>
 objectWithNoProperties:
"""
        self.run_test_with_schema(sample_schema, expected_output)

if __name__ == '__main__':
    unittest.main()
