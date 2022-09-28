import os
from unittest import main, TestCase

from gerund.components.config_txt import ConfigTxt

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = FILE_PATH.replace("components", "entry_points/meta_data/gerund.txt")


class TestConfigTxt(TestCase):

    def setUp(self) -> None:
        self.data_structure = {
            '[vars]': {'one': '1', 'two': 'two'},
            '[env_vars]': {'three': '3', 'four': 'four'},
            '[commands]': ['echo $three', 'echo $four', 'echo {=>one}'],
            '[meta]': {'output': 'result.txt'}
        }
        self.test = ConfigTxt(path=CONFIG_PATH)

    def tearDown(self) -> None:
        if os.path.isfile(f"{FILE_PATH}/output.txt"):
            os.remove(f"{FILE_PATH}/output.txt")

    def test___init__(self):
        expected_data_structure = {
            '[vars]': {},
            '[env_vars]': {},
            '[commands]': [],
            '[meta]': {}
        }
        self.assertEqual(CONFIG_PATH, self.test.path)
        self.assertEqual(expected_data_structure, self.test.data_structure)

    def test_read(self):
        self.test.read()
        self.assertEqual(self.data_structure, self.test.data_structure)

    def test_write(self):
        self.test.data_structure = self.data_structure
        self.test.write(f"{FILE_PATH}/output.txt")

        test = ConfigTxt(path=f"{FILE_PATH}/output.txt")
        test.read()
        self.assertEqual(self.data_structure, test.data_structure)

    def test_properties(self):
        self.test.read()
        self.assertEqual(self.data_structure['[vars]'], self.test.vars)
        self.assertEqual(self.data_structure['[env_vars]'], self.test.env_vars)
        self.assertEqual(self.data_structure['[commands]'], self.test.commands)
        self.assertEqual(self.data_structure['[meta]'], self.test.meta)


if __name__ == "__main__":
    main()
