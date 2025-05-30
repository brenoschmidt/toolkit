""" 
Utilities for the Toolkit for Finance course

         
"""
from __future__ import annotations

import tomllib
import pathlib
import os
import sys
import subprocess
from functools import lru_cache
import dataclasses as dc

try:
    import tk_utils_core
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
            f"{e}\n" 
            "Please open the PyCharm TERMINAL and type\n" 
            "   python tk_utils/setup.py"
            ) from e

from tk_utils.setup import (
        Setup,
        check_locs,
        )

# Probably overkill but just in case students import this module
# from _backup or _dropbox
check_locs()

def update():
    pass












