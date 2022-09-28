import os
from unittest import main, TestCase
from unittest.mock import patch

from gerund.entry_points.run_config import main as entry_main

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
OUTPUT_DIR = FILE_PATH + "/output.txt"


class TestRunConfig(TestCase):

    def setUp(self) -> None:
        self.config_data = {
          "output": "result.txt",
          "vars": {
            "one": 1,
            "two": "two"
          },
          "env_vars": {
            "three": "3",
            "four": "four"
          },
          "commands": [
            "echo $three",
            "echo $four",
            "echo {=>one}"
          ]
        }

    def tearDown(self) -> None:
        if os.path.isfile(OUTPUT_DIR):
            os.remove(OUTPUT_DIR)

    @patch("gerund.entry_points.run_config.argparse")
    @patch("gerund.entry_points.run_config.os")
    def test_full_yml(self, mock_os, mock_argparse):
        mock_os.getcwd.return_value = FILE_PATH
        mock_argparse.ArgumentParser.return_value.parse_args.return_value.f = "meta_data/gerund.yml"
        entry_main()

        with open(OUTPUT_DIR, "r") as file:
            data = file.read()
        self.assertEqual(['3', 'four', '1', ''], data.split("\n"))

    @patch("gerund.entry_points.run_config.argparse")
    @patch("gerund.entry_points.run_config.os")
    def test_full_json(self, mock_os, mock_argparse):
        mock_os.getcwd.return_value = FILE_PATH
        mock_argparse.ArgumentParser.return_value.parse_args.return_value.f = "meta_data/gerund.json"
        entry_main()

        with open(OUTPUT_DIR, "r") as file:
            data = file.read()
        self.assertEqual(['3', 'four', '1', ''], data.split("\n"))

    @patch("gerund.entry_points.run_config.argparse")
    @patch("gerund.entry_points.run_config.os")
    def test_full_txt(self, mock_os, mock_argparse):
        mock_os.getcwd.return_value = FILE_PATH
        mock_argparse.ArgumentParser.return_value.parse_args.return_value.f = "meta_data/gerund.txt"
        entry_main()

        with open(OUTPUT_DIR, "r") as file:
            data = file.read()
        self.assertEqual(['3', 'four', '1', ''], data.split("\n"))

    @patch("gerund.entry_points.run_config.TerminalCommand")
    @patch("gerund.entry_points.run_config.process_data_from_txt_file")
    @patch("gerund.entry_points.run_config.argparse")
    @patch("gerund.entry_points.run_config.os")
    def test_capture(self, mock_os, mock_argparse, mock_process_data_from_txt_file, terminal_command):

        mock_os.getcwd.return_value = FILE_PATH
        mock_argparse.ArgumentParser.return_value.parse_args.return_value.f = "meta_data/gerund.txt"
        del self.config_data["output"]
        mock_process_data_from_txt_file.return_value = self.config_data
        entry_main()

        terminal_command.assert_called_once_with(
            command=self.config_data["commands"],
            environment_variables=self.config_data["env_vars"],
            ip_address=None,
            key=None,
            username=None
        )
        terminal_command.return_value.wait.assert_called_once_with()

    @patch("gerund.entry_points.run_config.argparse")
    @patch("gerund.entry_points.run_config.os")
    def test_unsupported_file_format(self, mock_os, mock_argparse):
        mock_os.getcwd.return_value = FILE_PATH
        mock_argparse.ArgumentParser.return_value.parse_args.return_value.f = "meta_data/gerund.jest"

        with self.assertRaises(ValueError) as error:
            entry_main()
        self.assertEqual("jest is not supported", str(error.exception))


if __name__ == "__main__":
    main()
