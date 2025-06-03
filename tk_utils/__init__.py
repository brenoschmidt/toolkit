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

THIS_FILE = pathlib.Path(__file__)
TK_UTILS_DIR = THIS_FILE.parent
PRJ_DIR = TK_UTILS_DIR.parent
CONFIG_TOML = TK_UTILS_DIR.joinpath('config.toml')

# Update and localize defaults
tk_defaults = _dflts.load_toml_defaults(CONFIG_TOML)
_dflts.configure(tk_defaults)
defaults = _dflts.defaults

# Path validator
_tkpaths = tk_utils_core.pycharm.TKPaths(PRJ_DIR)
_sysutils = tk_utils_core.pycharm.SysUtils(_tkpaths)

if defaults.pycharm.validate_paths is True:
    _tkpaths.validate_tk_utils_init()

# Localize
sync_dbox = _sysutils.sync_dbox
copy_new_files = _sysutils.copy_new_files
backup = _sysutils.backup
update = _sysutils.update_tk_utils




