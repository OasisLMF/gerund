import os
from unittest import main, TestCase
from unittest.mock import patch

from gerund.commands.bash_script import BashScript


class TestBashScript(TestCase):

    def setUp(self) -> None:
        self.commands = [
            '#!/usr/bin/env bash',
            '',
            'SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"',
            'cd $SCRIPTPATH',
            '',
            'ls',
            'echo $ONE',
            '',
            'if [ -d "/path/to/dir" ]',
            'then',
            '    echo "Directory /path/to/dir exists"',
            'else',
            '    echo "Directory /path/to/dir does not exist"',
            'fi',
            '',
            ''
        ]

        self.read_path = str(os.path.dirname(os.path.realpath(__file__))) + "/meta_data/some_script.sh"
        self.write_path = str(os.path.dirname(os.path.realpath(__file__))) + "/meta_data/another_script.sh"
        self.path_test = BashScript(path=self.write_path)
        self.command_test = BashScript(commands=self.commands)

    def tearDown(self) -> None:
        pass

    def test__check_inputs(self):
        with self.assertRaises(ValueError) as error:
            BashScript()
        self.assertEqual("both commands and path cannot be None", str(error.exception))

    def test__read_script(self):
        self.assertEqual(self.commands, self.path_test.commands)

    @patch("gerund.commands.bash_script.open")
    def test__write_script(self, mock_open):
        self.path_test._commands = self.commands
        self.path_test._write_script()
        calls = mock_open.return_value.__enter__.return_value.write.call_args_list

        self.assertEqual(len(self.commands) * 2, len(calls))

        # loop through the commands inspecting calls to writing the file
        counter = 0
        rollover = True

        for i in calls:
            if rollover is True:
                self.assertEqual(self.commands[counter], i[0][0])
                counter += 1
                rollover = False
            else:
                self.assertEqual("\n", i[0][0])
                rollover = True

    @patch("gerund.commands.bash_script.TerminalCommand")
    @patch("gerund.commands.bash_script.Popen")
    def test__run_on_server(self, mock_open, mock_terminal_command):
        self.path_test.ip_address = "123456"
        key_path = "some_key.pem"
        self.path_test._run_on_server()

        command = f'scp {self.write_path} ubuntu@123456:/home/ubuntu/another_script.sh'
        mock_open.assert_called_once_with(command, shell=True)
        mock_open.return_value.wait.assert_called_once_with()

        mock_terminal_command.assert_called_once_with(
            command=['cd /home/ubuntu', 'sh another_script.sh', 'rm another_script.sh'],
            environment_variables=None, ip_address='123456', key=None, username='ubuntu'
        )
        mock_terminal_command.return_value.wait.assert_called_once_with(capture_output=False)

        mock_terminal_command.reset_mock()
        mock_open.reset_mock()

        self.path_test.key = key_path
        self.path_test._run_on_server()

        command = f'scp -i {key_path} {self.write_path} ubuntu@123456:/home/ubuntu/another_script.sh'
        mock_open.assert_called_once_with(command, shell=True)
        mock_open.return_value.wait.assert_called_once_with()

        mock_terminal_command.assert_called_once_with(
            command=['cd /home/ubuntu', 'sh another_script.sh', 'rm another_script.sh'],
            environment_variables=None, ip_address='123456', key=key_path, username='ubuntu'
        )
        mock_terminal_command.return_value.wait.assert_called_once_with(capture_output=False)

    @patch("gerund.commands.bash_script.datetime")
    def test__run(self, mock_datetime):
        mock_datetime.now.return_value.microsecond = "seconds"
        self.command_test.capture_output = True
        outcome = self.command_test._run()

        self.assertEqual(True, "bash_script.py" in outcome)
        self.assertEqual(True, "__init__.py" in outcome)
        self.assertEqual(True, "seconds.sh" in outcome)
        self.assertEqual(True, "terminal_command.py" in outcome)
        self.assertEqual(True, 'Directory /path/to/dir does not exist' in outcome)
        self.assertEqual(None, self.command_test._path)

        self.command_test.environment_variables = {"ONE": "some test"}
        outcome = self.command_test._run()

        self.assertEqual(True, "some test" in outcome)
        self.assertEqual(True, "bash_script.py" in outcome)
        self.assertEqual(True, "__init__.py" in outcome)
        self.assertEqual(True, "seconds.sh" in outcome)
        self.assertEqual(True, "terminal_command.py" in outcome)
        self.assertEqual(True, 'Directory /path/to/dir does not exist' in outcome)

        self.command_test.capture_output = False
        self.command_test._run()

    @patch("gerund.commands.bash_script.datetime")
    @patch("gerund.commands.bash_script.os")
    @patch("gerund.commands.bash_script.BashScript._run_on_server")
    @patch("gerund.commands.bash_script.BashScript._write_script")
    @patch("gerund.commands.bash_script.BashScript._run")
    def test_wait(self, mock__run, mock__write_script, mock__run_on_server, mock_os, mock_datetime):
        mock_datetime.now.return_value.microsecond = "seconds"
        mock_os.path.dirname.return_value = "base"
        outcome = self.path_test.wait()

        mock__run.assert_called_once_with()
        self.assertEqual(mock__run.return_value, outcome)

        self.path_test.ip_address = "123456"
        outcome = self.path_test.wait()
        mock__run_on_server.assert_called_once_with()
        self.assertEqual(mock__run_on_server.return_value, outcome)

        mock__run_on_server.reset_mock()
        self.path_test._path = None
        outcome = self.path_test.wait()

        self.assertEqual("base/seconds.sh", self.path_test._path)
        mock__write_script.assert_called_once_with()
        mock__run_on_server.assert_called_once_with()
        mock_os.remove.assert_called_once_with(self.path_test._path)
        self.assertEqual(mock__run_on_server.return_value, outcome)


if __name__ == "__main__":
    main()
