"""
This file defines the class that compiles and runs terminal commands locally or on a server.
"""
from subprocess import Popen, PIPE
from typing import Optional, List

from gerund.components.command_string import CommandString
from gerund.components.variable import Variable
from gerund.enums import InputCmd, EnvVars


class TerminalCommand:
    """
    This class is responsible for compiling a terminal command with environment variables and running it locally or on
    a server.

    Attributes:
        environment_variables (Optional[Dict[str, str]]): environment variables to be loaded into the command if present
        ip_address (Optional[str]): the IP address that the command is going to be run on if present
        key (Optional[str]): path to key however, not yet used
        username (str): the username for the server (default is "ubuntu")
    """
    def __init__(self, command: InputCmd, environment_variables: EnvVars = None,
                 ip_address: Optional[str] = None, key: Optional[str] = None,
                 username: str = "ubuntu") -> None:
        """
        The constructor for the TerminalCommand class.

        :param command: (Union[str, List[str]]) command or a series of commands to be run
        :param environment_variables: (Optional[Dict[str, str]]) environment variables to be loaded into the command
        :param ip_address: (Optional[str]) the IP address that the command is going to be run on if present
        :param key: (Optional[str]) path to key however, not yet used
        :param username: (str) the username for the server (default is "ubuntu")
        """
        self._process: Optional[Popen] = None
        self._command_str: Optional[str] = None
        self._command_buffer: Optional[List[str]] = None
        self._remote: Optional[bool] = None
        self.environment_variables: EnvVars = environment_variables
        self.ip_address: Optional[str] = ip_address
        self.key: Optional[str] = key
        self.username: str = username
        self._process_input(command=command)
        self._process_remote()

    def _process_input(self, command: InputCmd) -> None:
        """
        Populates the self._command_str or self._command_buffer depending on what was passed in

        :param command: (Union[str, List[str]]) command input to be processed
        :return: None
        """
        if isinstance(command, str):
            self._command_str = command
        elif isinstance(command, list):
            self._command_buffer = command
        else:
            raise ValueError(f"{type(command)} is not supported for a command")

    def _process_remote(self) -> None:
        """
        Defines if the command is a remote command or not based on the self.ip_address.

        :return: None
        """
        if self.ip_address is not None:
            self._remote = True
        elif self.key is not None and self.ip_address is None:
            raise ValueError("key supplied but IP address not supplied")
        else:
            self._remote = False

    def _process_variables(self) -> Optional[str]:
        """
        Packages the environment variables from self.environment_variables into a series of commands creating
        environment variables for the command session.

        :return: (Optional[str]) a string of commands that exports the variables as environment variables
        """
        if self.environment_variables is None:
            return None
        if len(self.environment_variables.keys()) == 0:
            return None

        buffer: List[str] = []

        for key in self.environment_variables.keys():
            variable: Variable = Variable(self.environment_variables[key])
            command: str = f'export {key}="{variable}"'
            buffer.append(command)
            buffer.append("&&")

        return " ".join(buffer[:-1])

    def _process_command(self) -> str:
        """
        Processes the input commands into a series of commands that can be executed in a process.

        :return: (str) the command can be executed in a command
        """
        if self._command_buffer is not None:
            return " && ".join(self._command_buffer)
        return self._command_str

    def _compile_command(self) -> str:
        """
        Compiles all the commands and environment variables into an executable command.

        :return: (str) the executable command for the entire process
        """
        buffer: List[str] = []
        vars_command: Optional[str] = self._process_variables()

        if self.key is None:
            command_prefix = "ssh -A -o StrictHostKeyChecking=no"
        else:
            command_prefix = f"ssh -A -o StrictHostKeyChecking=no -i '{self.key}'"

        # print(f"\n\n\n{command_prefix}\n\n\n")
        if self._remote is True:
            buffer.append(f"{command_prefix} {self.username}@{self.ip_address}")
            buffer.append("'")

        if vars_command is not None:
            buffer.append(vars_command)
            buffer.append("&&")
        buffer.append(str(CommandString(self._process_command())))

        if self._remote is True:
            buffer.append("'")
            buffer.append(" -y")
        return " ".join(buffer)

    def wait(self, capture_output: bool = False) -> Optional[List[str]]:
        """
        Compiles and runs the command.

        :param capture_output: (bool) if True, will capture output of the command
        :return: (Optional[List[str]])
        """
        compiled_command: str = self._compile_command()

        if capture_output is True:
            print(compiled_command)
            self._process = Popen(compiled_command, shell=True, stdout=PIPE)
            self._process.wait()
            return self._process.communicate()[0].decode().split("\n")[:-1]
        else:
            print(compiled_command)
            self._process = Popen(compiled_command, shell=True)
            self._process.wait()

    @property
    def process(self) -> Popen:
        return self._process
