import unittest

from os import path

from hvcc.generators.c2daisy.json2daisy import flatten_pin_dicts, flatten_index_dicts


# Grabbing the absolute path to test data
data_path = path.join(path.dirname(path.abspath(__file__)), 'data')


# A simple comparison for strings / literals / dicts within dicts
def compare_dicts(d1: dict, d2: dict) -> bool:
    for key, item in d1.items():
        try:
            if isinstance(item, dict):
                if not compare_dicts(item, d2[key]):
                    return False
            else:
                if item != d2[key]:
                    return False
        except (KeyError, IndexError) as e:
            print(f"Exception: {e}")
            return False
    return True


class TestFunctions(unittest.TestCase):

    def test_compare_dicts(self):
        d1_true = {'key1': 1, 'key2': {'nested_key': 2}}
        d2_true = {'key1': 1, 'key2': {'nested_key': 2}}
        d2_false = {'key1': 1, 'key2': {'nested_key': 3}}
        d2_false_2 = {'key1': 1}
        self.assertTrue(compare_dicts(d1_true, d2_true))
        self.assertFalse(compare_dicts(d1_true, d2_false))
        self.assertFalse(compare_dicts(d1_true, d2_false_2))

    def test_flatten_pin_dicts(self):
        input_component = {
            'name': 'example',
            'component': 'Switch',
            'pin': {'a': 1, 'b': 2},
            'index': {'a': 1, 'b': 2}
        }
        expected_output = {
            'name': 'example',
            'component': 'Switch',
            'pin_a': 1,
            'pin_b': 2,
            'index': {'a': 1, 'b': 2}
        }
        test_output = flatten_pin_dicts(input_component)
        self.assertTrue(compare_dicts(test_output, expected_output))

    def test_flatten_index_dicts(self):
        input_component = {
            'name': 'example',
            'component': 'Switch',
            'pin': {'a': 1, 'b': 2},
            'index': {'a': 1, 'b': 2}
        }
        expected_output = {
            'name': 'example',
            'component': 'Switch',
            'pin': {'a': 1, 'b': 2},
            'index_a': 1,
            'index_b': 2
        }
        test_output = flatten_index_dicts(input_component)
        self.assertTrue(compare_dicts(test_output, expected_output))
