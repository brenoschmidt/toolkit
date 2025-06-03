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
from types import SimpleNamespace
import pathlib
import subprocess
import shutil
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

def run(
        cmd: list[str], 
        shell: bool = False,
        err_msg: str = '') -> subprocess.CompletedProcess:
    """
    Run a shell command and raise RuntimeError if it fails.

    Parameters
    ----------
    cmd : list of str
        The command to run.
    shell : bool, default False
        If True, run command through the shell.
    err_msg : str, default ''
        Extra message to include if the command fails.

    Returns
    -------
    subprocess.CompletedProcess
        The result object with stdout, stderr, and returncode.
    """
    r = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell,
        text=True
    )
    if r.returncode != 0:
        msg = f"Command failed: {' '.join(cmd)}"
        if err_msg:
            msg += f"\n{err_msg}"
        msg += f"\n{r.stderr.strip()}"
        raise RuntimeError(msg)
    return r


def create_venv(
        env_dir: str | pathlib.Path,
        force: bool = False) -> bool:
    """
    Create a new virtual environment in the given directory if it does not exist.

    Parameters
    ----------
    env_dir : str | pathlib.Path
        The path to the virtual environment directory.
    force : bool, default False
        If True, forcibly deletes an existing directory before creating a new venv.

    Returns
    -------
    bool
        True if the environment was created, False if it was already active.
    """
    env_dir = env_dir if isinstance(env_dir, pathlib.Path) else pathlib.Path(env_dir)
    is_active = sys.prefix == str(env_dir.resolve())

    if is_active:
        print(f"Virtual environment already active: {env_dir}")
        return False

    pyvenv_cfg = env_dir / "pyvenv.cfg"
    if env_dir.exists():
        if pyvenv_cfg.exists():
            if force:
                print(f"Warning: Forcibly removing existing venv at {env_dir}")
                shutil.rmtree(env_dir)
            else:
                raise FileExistsError(
                    f"Directory '{env_dir}' contains a venv but it is not active.\n"
                    "Try restarting your IDE, or use force=True to recreate it."
                )
        else:
            raise FileExistsError(
                f"Directory '{env_dir}' exists but does not contain a venv.\n"
                "Use force=True to overwrite it."
            )

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
    pip_exec = venv_bin.joinpath('pip')
    pyexec = venv_bin.joinpath('python' if POSIX else 'python.exe')
    return SimpleNamespace(
            root=venv_dir,
            bin=venv_bin,
            pip=pip_exec,
            pyexec=pyexec,
            )

class Setup:
    """
    Virtual environment and dependency setup utility.
    """

    def __init__(self):
        self.config = mk_config()
        self.venv = mk_venv_opts()


    def mk_config(self) -> dict[str, Any]:
        """
        Load the configuration from `config.toml`.
        """
        with open(CONFIG_TOML, "rb") as f:
            return tomllib.load(f)

    def setup_venv(self, force: bool = False):
        """
        Set up the `.venv/` directory if not already present and active.
        """
        return create_env(env_dir=self.venv.root, force=force)

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
        if not self.venv.pip.exists():
            raise FileNotFoundError("Cannot find pip executable inside venv")

        opts = "--force-reinstall" if force_reinstall else ""
        tgt = self.tk_utils_core_url
        run_command(f"{self.venv.pip} install {opts} git+{tgt}")


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
