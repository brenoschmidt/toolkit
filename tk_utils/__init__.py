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

def _as_path(pth: str | pathlib.Path):
    return pth if isinstance(pth, pathlib.Path) else pathlib.Path(pth)


def _load_config_toml() -> dict[str, Any]:
    pth = pathlib.Path(__file__).joinpath('config.toml')
    if not pth.exists():
        raise FileNotFoundError(f"Cannot find config file: {pth}")
    with open(pth, "rb") as f:
        return tomllib.load(f)

_config_toml = _load_config_toml()

@dc.dataclass
def Directories:
    """
    Directories
    """
    toolkit: pathlib.Path
    backup: pathlib.Path
    dropbox: pathlib.Path
    venv: pathlib.Path











