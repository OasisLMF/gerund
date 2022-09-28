"""
This file defines the class that manages the txt file for the config file.
"""
from typing import Optional, List


class ConfigTxt:
    """
    This class is responsible for reading and writing command run function config txt files.

    Attributes:
        path (str): the path to the config file that is going to be read
        data_structure (dict): data around the command to be run
    """
    def __init__(self, path: str) -> None:
        """
        The constructor for the ConfigTxt class.

        :param path: (str) the path to the txt file that is going to be read
        """
        self.path: str = path
        self.data_structure: dict = {
            "[vars]": {},
            "[env_vars]": {},
            "[commands]": [],
            "[meta]": {}
        }
        self.buffer: List[str] = []

    def read(self) -> None:
        """
        Reads the txt config file populating the self.data_structure with the data read from the file.

        :return: None
        """
        with open(self.path, "r") as file:
            data = file.read()

        buffer = data.split("\n")
        headers = list(self.data_structure.keys())
        cached_header: Optional[str] = None

        for i in buffer:
            if i in headers:
                cached_header = i
            else:
                if i != "":
                    if cached_header == "[commands]":
                        self.data_structure[cached_header].append(i)
                    else:
                        split_var = i.split("=")
                        self.data_structure[cached_header][split_var[0]] = split_var[1]

    def write_line(self, line: str) -> None:
        """
        Writes a new line to the self.buffer.

        :param line: (str) the line to be written
        :return: None
        """
        self.buffer.append(line + "\n")

    def write_section(self, section_key: str) -> None:
        """
        Write an entire section from the self.data_structure to the self.buffer.

        :param section_key: (str) the key of the section to be written to
        :return: None
        """
        self.write_line(line=section_key)
        for key, value in self.data_structure[section_key].items():
            self.write_line(line=f"{key}={value}")

    def write(self, path: str) -> None:
        """
        Writes the self.data_structure to the txt file.

        :param path: (str) path to the txt file that is going to be written to
        :return: None
        """
        self.write_section(section_key="[meta]")
        self.write_line(line="")
        self.write_section(section_key="[vars]")
        self.write_line(line="")
        self.write_section(section_key="[env_vars]")
        self.write_line(line="")

        self.write_line(line="[commands]")
        for i in self.data_structure["[commands]"]:
            self.write_line(line=i)

        with open(path, "w") as file:
            for line in self.buffer:
                file.write(line)

    @property
    def meta(self) -> dict:
        return self.data_structure["[meta]"]

    @property
    def vars(self) -> dict:
        return self.data_structure["[vars]"]

    @property
    def env_vars(self) -> dict:
        return self.data_structure["[env_vars]"]

    @property
    def commands(self) -> dict:
        return self.data_structure["[commands]"]
