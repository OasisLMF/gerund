"""
This file defines the types and enums used in the package.
"""
from typing import Optional, Dict, List, Union


EnvVars = Optional[Dict[str, str]]
InputCmd = Union[str, List[str]]
