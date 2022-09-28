"""
This file defines the entry point for the command "gerund". This is the main entry point where a command is run
based off the config file that is loaded.

Example:
    gerund --f "/some/path/gerund_config.yml"
"""
import argparse
import json
import os

import yaml

from gerund.commands.terminal_command import TerminalCommand
from gerund.components.config_txt import ConfigTxt
from gerund.components.local_variable_storage import LocalVariableStorage


def process_data_from_txt_file(path: str) -> dict:
    """
    Loads the data from the txt config file and packages the loaded data into a format for the company.

    :param path: (str) the path for the txt config file
    :return: (dict) the packaged config data
    """
    config = ConfigTxt(path=path)
    config.read()
    data = dict()

    data["output"] = config.meta.get("output")
    data["ip_address"] = config.meta.get("ip_address")
    data["key"] = config.meta.get("key")
    data["username"] = config.meta.get("username")

    data["vars"] = config.vars
    data["commands"] = config.commands
    data["env_vars"] = config.env_vars
    return data


def process_data(file_path: str, file_type: str) -> dict:
    """
    Extracts the data from the config file.

    :param file_path: (str) the path to the config file
    :param file_type: (str) the type of file being loaded
    :return: (dict) the data from the config file
    """
    if file_type in ["yml", "yaml"]:
        with open(file_path, "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
    elif file_type == "json":
        with open(file_path, "r") as file:
            data = json.loads(file.read())
    elif file_type == "txt":
        data = process_data_from_txt_file(path=file_path)
    else:
        raise ValueError(f"{file_type} is not supported")
    return data


def main() -> None:
    """
    This function runs the entry point reading a config file and running a series of commands with environment
    variables and configurations around username, ip_address, keys etc.

    :return:
    """
    config_parser = argparse.ArgumentParser()
    config_parser.add_argument('--f', action='store', type=str, required=False, default="gerund.yml",
                               help="the path the config yml/json/txt file that defines the command run"
                                    "(default: gerund.yml)")

    args = config_parser.parse_args()

    file_type = args.f.split(".")[-1]
    file_path = f"{os.getcwd()}/{args.f}"

    data = process_data(file_path=file_path, file_type=file_type)

    local_vars = data.get("vars")
    if local_vars is not None:
        local_storage = LocalVariableStorage()
        local_storage.update(local_vars)

    output = data.get("output")
    if output is not None:
        capture = True
    else:
        capture = False

    command = TerminalCommand(command=data["commands"],
                              environment_variables=data.get("env_vars"),
                              ip_address=data.get("ip_address"),
                              key=data.get("key"),
                              username=data.get("username"))
    if capture is True:
        data = command.wait(capture_output=True)
        with open(f"{os.getcwd()}/output.txt", "w") as file:
            for line in data:
                file.write(line + "\n")
    else:
        command.wait()
