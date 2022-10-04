"""
This file defines the mechanisms around running a bash script either locally or on a server.
"""
import os
from datetime import datetime
from subprocess import Popen
from typing import List, Optional

from gerund.commands.terminal_command import TerminalCommand
from gerund.enums import EnvVars


class BashScript:
    """
    This class is responsible for running bash scripts which can either be local or on a server.

    Attributes:
        environment_variables (EnvVars): the environment variables that will be applied to the bash script
        ip_address (Optional[str]): IP address of the server to run the bash script if running on server
        key (Optional[str]): path to pem key if needed to be run on server
        username (str): the username of the server which has a default of "ubuntu"
        capture_output (bool): for the output to be captured with a default of False
    """
    def __init__(self, commands: Optional[List[str]] = None, path: Optional[str] = None,
                 environment_variables: EnvVars = None, ip_address: Optional[str] = None, key: Optional[str] = None,
                 username: str = "ubuntu", capture_output: bool = False) -> None:
        """
        The constructor for the BashScript class.

        Args:
            commands: (Optional[List[str]]) each element is a line in a bash script
            path: (Optional[str]) path to bash script to be written or read
            environment_variables: (EnvVars) environment variables to be applied when running bash script
            ip_address: (Optional[str]) IP address of the server to run the bash script if running on server
            key: (Optional[str]) path to pem key if needed to be run on server
            username: (str) the username of the server which has a default of "ubuntu"
            capture_output: (bool) for the output to be captured with a default of False
        """
        self._commands: Optional[List[str]] = commands
        self._path: Optional[str] = path
        self._check_inputs()
        self.environment_variables: EnvVars = environment_variables
        self.ip_address: Optional[str] = ip_address
        self.key: Optional[str] = key
        self.username: str = username
        self.capture_output: bool = capture_output

    def _check_inputs(self) -> None:
        """
        Ensures that both self._path and self._commands are not None raising an error if not.

        Returns: None
        """
        if self._commands == self._path and self._path is None:
            raise ValueError("both commands and path cannot be None")

    def _read_script(self) -> None:
        """
        Reads a bash script from the self._path.

        Returns: None
        """
        with open(self._path, "r") as file:
            self._commands = file.read().split("\n")

    def _write_script(self) -> None:
        """
        Writes the self.commands to self._path.

        Returns: None
        """
        with open(self._path, "w") as file:
            for i in self.commands:
                file.write(i)
                file.write("\n")

    def _run_on_server(self) -> Optional[List[str]]:
        """
        Copies the bash script or commands onto a server, runs them, and then wipes the script from the server.

        Returns: (Optional[List[str]]) captured output from the script if self.capture_output is True
        """
        script_name = self._path.split("/")[-1]
        if self.key is None:
            command = f"scp {self._path} ubuntu@{self.ip_address}:/home/{self.username}/{script_name}"
        else:
            command = f"scp -i {self.key} {self._path} ubuntu@{self.ip_address}:/home/{self.username}/{script_name}"

        # copy script onto server
        copy_to_server = Popen(command, shell=True)
        copy_to_server.wait()

        # run the terminal command
        run_script = TerminalCommand(command=[f"cd /home/{self.username}", f"sh {script_name}", f"rm {script_name}"],
                                     environment_variables=self.environment_variables,
                                     ip_address=self.ip_address, key=self.key, username=self.username)
        return run_script.wait(capture_output=self.capture_output)

    def _run(self) -> Optional[List[str]]:
        """
        Runs a bash script locally.

        Returns: (Optional[List[str]]) captured output from the script if self.capture_output is True
        """
        cache_path = str(os.path.dirname(os.path.realpath(__file__))) + f"/{datetime.now().microsecond}.sh"
        _ = self.commands
        cached_path = self._path
        self._path = cache_path
        self._write_script()

        command = TerminalCommand(command=f"sh {self._path}", environment_variables=self.environment_variables)
        output = None
        if self.capture_output is True:
            output = command.wait(capture_output=True)
        else:
            command.wait()
        os.remove(self._path)
        self._path = cached_path
        return output

    def wait(self) -> Optional[List[str]]:
        """
        Runs the bash script either locally or on a server base on attributes.

        Returns: (Optional[List[str]]) captured output from the script if self.capture_output is True
        """
        if self.ip_address is None:
            return self._run()
        if self._path is None:
            self._path = str(os.path.dirname(os.path.realpath(__file__))) + f"/{datetime.now().microsecond}.sh"
            self._write_script()
            outcome = self._run_on_server()
            os.remove(self._path)
        else:
            outcome = self._run_on_server()
        return outcome

    @property
    def commands(self) -> List[str]:
        if self._commands is None:
            self._read_script()
        return self._commands
