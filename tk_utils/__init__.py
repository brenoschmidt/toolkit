""" 
Utilities for the Toolkit for Finance course

         
"""
from __future__ import annotations

import pathlib

try:
    import tk_utils_core
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
            f"{e}\n" 
            "Please open the PyCharm TERMINAL and type\n" 
            "   python tk_utils/setup.py"
            ) from e

from tk_utils_core import options as _dflts
from tk_utils_core import (
        converters,
        decorators,
        messages,
        pycharm,
        system,
        structs,
        validators,
        webtools,
        )

__version__ = "0.2.1"
__all__ = [
        'backup',
        'converters',
        'copy_new_files',
        'decorators',
        'messages',
        'options',
        'pycharm',
        'structs',
        'sync_dbox',
        'system',
        'tk_utils_core',
        'update',
        'validators',
        'webtools',
        'describe',
        ]

THIS_FILE = pathlib.Path(__file__)
TK_UTILS_DIR = THIS_FILE.parent
PRJ_DIR = TK_UTILS_DIR.parent
CONFIG_TOML = TK_UTILS_DIR.joinpath('config.toml')

# Update and localize defaults
tk_options = _dflts.load_toml_defaults(CONFIG_TOML)
_dflts.configure(tk_options)
options = _dflts.options

# Path validator
_tkpaths = pycharm.TKPaths(PRJ_DIR)
_sysutils = pycharm.SysUtils(_tkpaths)

if options.pycharm.validate_paths is True:
    _tkpaths.validate_tk_utils_init()
    _tkpaths.validate_venv()

# ----------------------------------------------------------------------------
#   Localize 
# ----------------------------------------------------------------------------
sync_dbox = _sysutils.sync_dbox
copy_new_files = _sysutils.copy_new_files
backup = _sysutils.backup
update = _sysutils.update_tk_utils

# Decorators
describe = decorators.describe




