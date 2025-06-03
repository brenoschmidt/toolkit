""" 
Utilities for the Toolkit for Finance course

         
"""
from __future__ import annotations

import tomllib
import pathlib
import os
import sys
from functools import lru_cache

try:
    import tk_utils_core
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
            f"{e}\n" 
            "Please open the PyCharm TERMINAL and type\n" 
            "   python tk_utils/setup.py"
            ) from e

from tk_utils_core import defaults as _dflts
from tk_utils_core import *

CONFIG_TOML = pathlib.Path(__file__).parent.joinpath('config.toml')

tk_defaults = _dflts.load_toml_defaults(CONFIG_TOML)
_dflts.configure(tk_defaults)

# Localize defaults
defaults = _dflts.defaults



print(dir(sys.version))


