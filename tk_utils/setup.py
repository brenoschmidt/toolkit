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

from functools import cached_property
from collections import namedtuple
import os
from types import SimpleNamespace
import shlex
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
        cmd: list[str] | str,
        shell: bool = True,
        quiet: bool = False,
        echo: bool = False,
        bufsize: int = 0,
        err_msg: str = '',
        **kargs: Any) -> namedtuple:
    """
    Run a shell or subprocess command and capture output.

    Parameters
    ----------
    cmd : list[str] | str
        Command to run.

    shell : bool, default True
        If True, run the command via the shell.

    quiet : bool, default False
        If True, do not print stdout.

    echo : bool, default False
        If True, print the command being executed.

    bufsize : int, default 0
        Buffer size passed to subprocess.Popen.

    err_msg : str, default ''
        Extra message to include if the command fails.

    **kargs : Any
        Passed to subprocess.Popen.

    Returns
    -------
    Result
        Named tuple with fields: cmd, stdout, stderr, rc (return code).
    """
    Result = namedtuple('Result', ['cmd', 'stdout', 'stderr', 'rc'])

    cmd_list = cmd if isinstance(cmd, list) else shlex.split(cmd)
    cmd_str = ' '.join(cmd_list) if shell else cmd_list

    if echo:
        print(f"Running: {cmd_str}")

    proc = subprocess.Popen(
        cmd_str,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=bufsize,
        **kargs,
    )
    out, err = proc.communicate()
    rc = proc.returncode

    out_str = out.decode('utf-8') if out else ''
    err_str = err.decode('utf-8') if err else ''

    if not quiet and out_str:
        print(out_str)

    if rc != 0:
        msg = f"Command failed [{rc}]: {cmd_str}"
        if err_msg:
            msg += f"\n{err_msg}"
        msg += f"\n{err_str.strip()}"
        raise RuntimeError(msg)

    return Result(cmd=cmd_str, stdout=out_str.splitlines(),
                  stderr=err_str.splitlines(), rc=rc)



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

    print(f"[done] Virtual environment created: {env_dir}")
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
        self.config = self.mk_config()
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
        return create_venv(env_dir=self.venv.root, force=force)

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
        run(f"{self.venv.pip} install {opts} git+{tgt}")


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
    s.setup_venv(force=False)
    s.install_tk_utils_core()
    print('--------------------------------')
    print('PLEASE RESTART PYCHARM NOW')
    print('--------------------------------')


if __name__ == "__main__":
    main()
