"""
This file defines a dict that holds local storage for variables.
"""


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LocalVariableStorage(dict, metaclass=Singleton):

    def __init__(self) -> None:
        super().__init__({})
