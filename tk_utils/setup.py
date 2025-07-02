"""
Setup a virtual environment for PyCharm and install required libraries.

This script is intended to be placed under a PyCharm project folder.  It
ensures the existence of a `.idea/` folder and a `config.toml` file, then sets
up a `.venv/` virtual environment and installs the `tk_utils_core` package
from GitHub.

toolkit/                        <- PyCharm project folder
|__ tk_utils/     
|   |__ __init__.py             
|   |__ config.toml
|   |__ setup.py                <- This file


Usage
-----
Run this script directly inside a PyCharm-managed project:

    $ python tk_utils/setup.py

"""
from __future__ import annotations

import argparse
from collections import namedtuple
from functools import cached_property
from types import SimpleNamespace
from typing import Any, Sequence
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import textwrap
import tomllib

THIS_FILE = pathlib.Path(__file__)
THIS_DIR = THIS_FILE.parent
PROJECT_ROOT = THIS_DIR.parent
CONFIG_TOML = THIS_DIR.joinpath('config.toml')
POSIX = os.name == 'posix'
RETRY_MSG = (
            "To resolve this issue:\n"
            "  1. Restart PyCharm\n"
            "  2. If the problem persists, try running this script with"
            " the --force flag:\n"
            "     python tk_utils/setup.py --force"
            )

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

def run(
        cmds: Sequence[str],
        err_msg: str = '',
        echo: bool = False,
        quiet: bool = False) -> None:
    """
    Run a subprocess command safely (shell=False).

    Parameters
    ----------
    cmds : list[str]
        Command and arguments to run (e.g. ['ls', '-l'])

    err_msg : str
        Extra message to append if command fails.

    echo : bool
        If True, prints the command being run.

    quiet : bool
        If True, suppresses stdout on success.
    """
    if not isinstance(cmds, (list, tuple)):
        raise TypeError(
                f"`cmds` must be a list or tuple of strings, got: {type(cmds)}")

    if echo:
        print(f"Running: {' '.join(cmds)}")

    r = subprocess.run(
        cmds,
        shell=False,
        capture_output=True,
        text=True,
        check=False,
    )

    if r.returncode != 0:
        msg = r.stderr.strip()
        if err_msg:
            msg = f"{err_msg}\n{msg}"
        raise RuntimeError(msg)

    if not quiet and r.stdout:
        print(r.stdout, end='')

def create_venv(
        env_dir: str | pathlib.Path,
        force: bool = False) -> bool:
    """
    Create a new virtual environment in the given directory if it does not exist.

    This function checks whether the specified environment is:
    - Already the active virtual environment (in which case, nothing is done).
    - An existing directory with a valid venv (raises unless `force=True`).
    - A non-existent path (creates a new virtual environment using `python -m venv`).

    Parameters
    ----------
    env_dir : str | pathlib.Path
        The path to the virtual environment directory.

    force : bool, default False

        If True, forcibly deletes an existing directory before creating a new
        venv. Only if env_dir.name == '.venv'

    """
    env_dir = env_dir if isinstance(env_dir, pathlib.Path) else pathlib.Path(env_dir)
    is_active = sys.prefix == str(env_dir)

    if is_active:
        print(f"Virtual environment already active: {env_dir}")
        return False

    pyvenv_cfg = env_dir / "pyvenv.cfg"
    if env_dir.exists():
        if force and env_dir.name == '.venv':
            print(f"Warning: Forcibly removing existing venv at {env_dir}")
            shutil.rmtree(env_dir)
        elif pyvenv_cfg.exists():
            raise FileExistsError(
                f"Directory '{env_dir}' contains a venv but it is not active.\n"
                + RETRY_MSG)
        else:
            raise FileExistsError(
                f"Directory '{env_dir}' exists but does not contain a venv.\n"
                + RETRY_MSG)

    print(f"Creating virtual environment at {env_dir}")
    run(
        [sys.executable, "-m", "venv", str(env_dir)],
        err_msg=f"Failed to create virtual environment at {env_dir}"
    )

    print(f"Virtual environment created: {env_dir}")
    return True

def mk_venv_opts() -> SimpleNamespace:
    """
    """
    venv_dir = PROJECT_ROOT.joinpath('.venv')
    venv_bin = venv_dir.joinpath('bin' if POSIX else 'Scripts')
    # possible executable names (in order or priority)
    if POSIX:
        _pips = ['pip', 'pip3']
    else:
        _pips = ['pip.exe', 'pip3.exe', 'pip', 'pip3']
    pips = [venv_bin.joinpath(x) for x in _pips]
    return SimpleNamespace(
            root=venv_dir,
            bin=venv_bin,
            pips=pips,
            )

class Setup:
    """
    Virtual environment and dependency setup utility.
    """

    def __init__(self):
        self.config = self.mk_config()
        self.venv = mk_venv_opts()

    def mk_config(self) -> dict[str, Any]:
        """
        Load the configuration from `config.toml`.
        """
        with open(CONFIG_TOML, "rb") as f:
            return tomllib.load(f)

    def get_pip(self) -> pathlib.Path | None:
        """
        Returns an existing pip executable (None if 
        no executable can be found
        """
        for p in self.venv.pips:
            if p.exists() and p.is_file():
                return p

    def setup_venv(self, force: bool = False):
        """
        Set up the `.venv/` directory if not already present and active.
        """
        return create_venv(env_dir=self.venv.root, force=force)

    @cached_property
    def tk_utils_core_url(self) -> str:
        """
        Construct GitHub URL to install `tk_utils_core`.
        """
        info = self.config['github']['tk_utils_core']
        return f"https://github.com/{info['user']}/{info['repo']}.git"

    def install_tk_utils_core(
            self, 
            force_reinstall: bool = True,
            branch: str | None = None):
        """
        Install `tk_utils_core` into the virtual environment.
        If `force_reinstall` is True, reinstallation is forced.
        """
        pipexec = self.get_pip() # -> pathlib.Path | None
        if pipexec is None or not pipexec.exists():
            raise FileNotFoundError("Cannot find pip executable inside venv")
        tgt = self.tk_utils_core_url
        if branch: 
            tgt = f"{tgt}@{branch}"

        cmd = [str(pipexec), "install"]
        if force_reinstall:
            cmd.append("--force-reinstall")
        cmd.append(f"git+{tgt}")
        run(cmd)

    def update_tk_utils_core(self):
        """
        Force reinstall of `tk_utils_core`.
        """
        self.install_tk_utils_core(force_reinstall=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Setup the virtual environment and install tk_utils_core."
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force setup even if a venv already exists but is not active.'
    )
    parser.add_argument(
        '--branch',
        type=str,
        help='Specify the git branch to use.'
    )
    return parser.parse_args()


def main():
    """
    Entrypoint for setting up the virtual environment and installing deps.
    """
    args = parse_args()

    check_locs()
    s = Setup()
    s.setup_venv(force=args.force)
    s.install_tk_utils_core(branch=args.branch)

    print('--------------------------------')
    print('PLEASE RESTART PYCHARM NOW')
    print('--------------------------------')


if __name__ == '__main__':
    main()
