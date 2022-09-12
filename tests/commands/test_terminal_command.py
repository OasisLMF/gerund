import pathlib
from unittest import main, TestCase
from unittest.mock import patch

from gerund.commands.terminal_command import TerminalCommand
from gerund.components.local_variable_storage import Singleton, LocalVariableStorage


class TestTerminalCommand(TestCase):

    def setUp(self) -> None:
        self.test = TerminalCommand(command="test")
        self.env_vars = {
            "ONE": "1",
            "TWO": "two",
            "THREE": "3"
        }
        self.ip_address = "123456"
        self.key = "remote.pem"
        storage = LocalVariableStorage()
        self.filepath = pathlib.Path(__file__).resolve().parent
        storage.update({
            "FOUR": "four",
            "SCRIPT_PATH": f"{self.filepath}/run_test.py"
        })

    def tearDown(self) -> None:
        Singleton._instances = {}

    def test___init__(self):
        test = TerminalCommand("test")

        self.assertEqual(None, test._process)
        self.assertEqual("test", test._command_str)
        self.assertEqual(None, test._command_buffer)
        self.assertEqual(False, test._remote)
        self.assertEqual(None, test.environment_variables)
        self.assertEqual(None, test.ip_address)
        self.assertEqual(None, test.key)

        test = TerminalCommand(["one", "two", "three"])

        self.assertEqual(None, test._process)
        self.assertEqual(None, test._command_str)
        self.assertEqual(["one", "two", "three"], test._command_buffer)
        self.assertEqual(False, test._remote)
        self.assertEqual(None, test.environment_variables)
        self.assertEqual(None, test.ip_address)
        self.assertEqual(None, test.key)

        test = TerminalCommand("test", environment_variables=self.env_vars, ip_address=self.ip_address, key=self.key)

        self.assertEqual(None, test._process)
        self.assertEqual("test", test._command_str)
        self.assertEqual(None, test._command_buffer)
        self.assertEqual(True, test._remote)
        self.assertEqual(self.env_vars, test.environment_variables)
        self.assertEqual(self.ip_address, test.ip_address)
        self.assertEqual(self.key, test.key)

        with self.assertRaises(ValueError) as error:
            TerminalCommand("test", key=self.key)

        self.assertEqual("key supplied but IP address not supplied", str(error.exception))

        with self.assertRaises(ValueError) as error:
            TerminalCommand(24, key=self.key)

        self.assertEqual("<class 'int'> is not supported for a command", str(error.exception))

    def test__process_variables(self):
        self.test.environment_variables = self.env_vars
        self.assertEqual('export ONE="1" && export TWO="two" && export THREE="3"', self.test._process_variables())

        self.test.environment_variables["FOUR"] = "=>FOUR"
        self.assertEqual('export ONE="1" && export TWO="two" && export THREE="3" && export FOUR="four"',
                         self.test._process_variables())

        self.test.environment_variables = None
        self.assertEqual(None, self.test._process_variables())

    def test__process_command(self):
        test = TerminalCommand("test")
        self.assertEqual("test", test._process_command())

        test = TerminalCommand(["one", "two", "three"])
        self.assertEqual("one && two && three", test._process_command())

    def test__compile_command(self):
        test = TerminalCommand("test", environment_variables=self.env_vars)
        expected_outcome = 'export ONE="1" && export TWO="two" && export THREE="3" && test'
        self.assertEqual(expected_outcome, test._compile_command())

        test = TerminalCommand("test", environment_variables=self.env_vars, ip_address=self.ip_address)
        expected_outcome = """ssh -A -o StrictHostKeyChecking=no ubuntu@123456 ' export ONE="1" && export """
        expected_outcome += """TWO="two" && export THREE="3" && test '"""
        self.assertEqual(expected_outcome, test._compile_command())

    def test_wait(self):
        test = TerminalCommand(f"python {self.filepath}/run_test.py", environment_variables=self.env_vars)
        self.assertEqual(['1', 'two'], test.wait(capture_output=True))

        test = TerminalCommand("python {=>SCRIPT_PATH}", environment_variables=self.env_vars)
        self.assertEqual(['1', 'two'], test.wait(capture_output=True))

        test = TerminalCommand([f"python {self.filepath}/run_test.py", "echo 'test'"],
                               environment_variables=self.env_vars)
        self.assertEqual(['1', 'two', 'test'], test.wait(capture_output=True))

    @patch("gerund.commands.terminal_command.Popen")
    def test_wait_none_capture(self, mock_p_open):
        test = TerminalCommand(f"python {self.filepath}/run_test.py")
        self.assertEqual(None, test.wait())
        mock_p_open.assert_called_once_with(f"python {self.filepath}/run_test.py", shell=True)
        mock_p_open.return_value.wait.assert_called_once_with()

    def test_process_attribute(self):
        self.test._process = "test"
        self.assertEqual("test", self.test.process)


if __name__ == "__main__":
    main()
