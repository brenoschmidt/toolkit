"""
Setup a virtual environment for PyCharm and install required libraries.

This script is intended to be placed under a PyCharm project folder.  It
ensures the existence of a `.idea/` folder and a `config.toml` file, then sets
up a `.venv/` virtual environment and installs the `tk_utils_core` package
from GitHub.

Usage
-----
Run this script directly inside a PyCharm-managed project:

    $ python tk_utils/setup.py

"""
from __future__ import annotations

from functools import cached_property
import os
import pathlib
import subprocess
import sys
import textwrap
import tomllib
from typing import Any

THIS_FILE = pathlib.Path(__file__)
THIS_DIR = THIS_FILE.parent
PROJECT_ROOT = THIS_DIR.parent
CONFIG_TOML = THIS_DIR.joinpath('config.toml')
POSIX = os.name == 'posix'


def _mk_dirtree(
        init_note: str = '',
        config_note: str = '',
        setup_note: str = '',
        ) -> str:
    tk_dir = "<- Must be under PyCharm's project folder"
    return textwrap.dedent(f'''\
    <PYCHARM_PROJECT_FOLDER>/
    |__ {THIS_DIR.name}/         {tk_dir}
    |   |__ __init__.py   {init_note}
    |   |__ {CONFIG_TOML.name}   {config_note}
    |   |__ {THIS_FILE.name}      {setup_note}
    ''')


def _as_path(pth: str | pathlib.Path) -> pathlib.Path:
    return pth if isinstance(pth, pathlib.Path) else pathlib.Path(pth)


def has_idea_folder(pth: pathlib.Path) -> bool:
    """
    True if the folder `pth` has a .idea sub-folder.
    """
    return pth.is_dir() and pth.joinpath('.idea').is_dir()


def check_locs():
    """
    Ensure the correct location of files and folders.
    Raises informative errors if `.idea/` or `config.toml` is missing.
    """
    if not has_idea_folder(PROJECT_ROOT):
        err = [
            "tk_utils should be inside a PyCharm project folder:",
            '',
            _mk_dirtree(setup_note='<- This file'),
        ]
        raise Exception('\n'.join(err))
    elif not CONFIG_TOML.exists():
        err = [
            f"Could not find '{CONFIG_TOML.name}' file.",
            '',
            _mk_dirtree(setup_note='<- This file',
                        config_note='<- Missing file'),
        ]
        raise FileNotFoundError('\n'.join(err))


def run_command(command: str):
    """
    Run a shell command and raise RuntimeError if it fails.
    """
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {command}")


class Setup:
    """
    Virtual environment and dependency setup utility.
    """

    @cached_property
    def config(self) -> dict[str, Any]:
        """
        Load the configuration from `config.toml`.
        """
        with open(CONFIG_TOML, "rb") as f:
            return tomllib.load(f)

    @cached_property
    def venv_dir(self) -> pathlib.Path:
        return PROJECT_ROOT.joinpath('.venv')

    @cached_property
    def venv_bin(self) -> pathlib.Path:
        return self.venv_dir.joinpath('bin' if POSIX else 'Scripts')

    @cached_property
    def pip_exec(self) -> pathlib.Path:
        return self.venv_bin.joinpath('pip')

    @cached_property
    def venv_exec(self) -> pathlib.Path:
        return self.venv_bin.joinpath('python' if POSIX else 'python.exe')

    def is_venv_activated(self) -> bool:
        """
        Check if the current Python interpreter is the one in the `.venv`.
        """
        return sys.prefix == str(self.venv_dir.resolve())

    def setup_venv(self):
        """
        Set up the `.venv/` directory if not already present and active.
        """
        if self.is_venv_activated():
            print("Virtual environment is setup and activated")
        elif self.venv_dir.exists():
            raise FileExistsError(
                f"Directory {self.venv_dir.name} exists but venv is not active\n"
                "Try restarting PyCharm\n"
                "If the error persists, configure the PyCharm interpreter manually"
            )
        else:
            run_command(f"{sys.executable} -m venv {self.venv_dir}")
            print("Virtual env created")

    @cached_property
    def tk_utils_core_url(self) -> str:
        """
        Construct GitHub URL to install `tk_utils_core`.
        """
        info = self.config['github']['tk_utils_core']
        return f"https://github.com/{info['user']}/{info['repo']}.git"

    def install_tk_utils_core(self, force_reinstall: bool = False):
        """
        Install `tk_utils_core` into the virtual environment.
        If `force_reinstall` is True, reinstallation is forced.
        """
        if not self.pip_exec.exists():
            raise FileNotFoundError("Cannot find pip executable inside venv")

        opts = "--force-reinstall" if force_reinstall else ""
        tgt = self.tk_utils_core_url
        run_command(f"{self.pip_exec} install {opts} git+{tgt}")

    def update_tk_utils_core(self):
        """
        Force reinstall of `tk_utils_core`.
        """
        self.install_tk_utils_core(force_reinstall=True)


def main():
    """
    Entrypoint for setting up the virtual environment and installing deps.
    """
    check_locs()
    s = Setup()
    s.setup_venv()
    s.install_tk_utils_core()
    print('--------------------------------')
    print('PLEASE RESTART PYCHARM NOW')
    print('--------------------------------')


if __name__ == "__main__":
    main()
