""" 
Setup virtual environment in PyCharm and install required libs

         
"""
from __future__ import annotations

import tomllib
import pathlib
import os
import sys
import subprocess
import textwrap
from functools import cached_property

THIS_FILE = pathlib.Path(__file__)
THIS_DIR = THIS_FILE.parent
PROJECT_ROOT = THIS_DIR.parent
CONFIG_TOML = THIS_DIR.joinpath('config.toml')
POSIX = os.name == 'posix'


def _mk_dirtree(
        init_note: str = '',
        config_note: str = '',
        setup_note: str = '',
        ):
    tk_dir = "<- Must be under PyCharm's project folder"
    return textwrap.dedent(f'''\
    <PYCHARM_PROJECT_FOLDER>/
    |__ {THIS_DIR.name}/         {tk_dir}
    |   |__ __init__.py   {init_note}
    |   |__ {CONFIG_TOML.name}   {config_note}
    |   |__ {THIS_FILE.name}      {setup_note}
    ''')


def _as_path(pth: str | pathlib.Path):
    return pth if isinstance(pth, pathlib.Path) else pathlib.Path(pth)

def has_idea_folder(pth: pathlib.Path) -> bool:
    """
    True if the folder `pth` has a .idea sub-folder
    """
    return pth.is_dir() and pth.joinpath('.idea').is_dir()


def check_locs():
    """
    Ensure the correct location of files and folders
    """
    if not has_idea_folder(PROJECT_ROOT):
        err = [
        "tk_utils should be inside a PyCharm project folder:",
        '',
        _mk_dirtree(setup_note='<- This file'),
        ]
        raise Exception('\n'.join(err))
    elif not CONFIG_TOML.exists():
        err  = [
        f"Could not find '{CONFIG_TOML.name}' file.",
        '',
        _mk_dirtree(setup_note='<- This file', 
                    config_note='<- Missing file'),
        ]
        raise FileNotFoundError('\n'.join(err))

def run_command(command):
    """Run a shell command and handle errors."""
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print("Error: Command failed.")
        sys.exit(1)

class Setup:
    """
    """

    @cached_property
    def config(self) -> dict[str, Any]:
        with open(CONFIG_TOML, "rb") as f:
            return tomllib.load(f)

    @cached_property
    def venv_dir(self) -> pathlib.Path:
        return PROJECT_ROOT.joinpath(
                self.config['dirnames']['venv'])


    @cached_property
    def venv_bin(self) -> pathlib.Path:
        if POSIX is True:
            return self.venv_dir.joinpath('bin')
        else:
            return self.venv_dir.joinpath('Scripts')

    @cached_property
    def pip_exec(self) -> pathlib.Path:
        return self.venv_bin.joinpath('pip')

    @cached_property
    def venv_exec(self) -> pathlib.Path:
        if POSIX is True:
            exec_name = 'python'
        else:
            exec_name = 'python.exe'
        return self.venv_bin.joinpath(exec_name)

    def is_venv_activated(self) -> bool:
        return pathlib.Path(sys.executable).resolve() \
                == self.venv_exec.resolve()

    def setup_venv(self):
        """
        """
        if self.is_venv_activated():
            print("Virtual environment is setup and activated")
        elif self.venv_dir.exists():
            raise FileExistsError(
                f"Directory {self.venv_dir.name} exists but venv is not active\n"
                "Try restarting PyCharm\n"
                "If the error persists, configure the PyCharm interpreter"
                )
        else:
            run_command(f"{sys.executable} -m venv {self.venv_dir}")
            print(f"Virtual env created")

    @cached_property
    def tk_utils_core_pkg(self) -> str:
        """
        """
        return "git+" + self.config['tk_utils_core']['github']


    def install_tk_utils_core(
            self,
            force_reinstall: bool = False):
        """
        """
        if not self.pip_exec.exists():
            raise Exception(f"Cannot find pip executable inside venv")
        opts = ''
        if force_reinstall is True:
            opt = f"{opts} --force-reinstall"
        tgt = self.tk_utils_core_pkg
        run_command(f"{self.pip_exec} install {opts} {tgt}"))


    def update_tk_utils_core(self):
        self.install_tk_utils_core(force_reinstall=True)


def main():
    """
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

