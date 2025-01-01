from __future__ import annotations

import subprocess
import os
import pwd
from abc import ABC, abstractmethod
from typing import Callable
from io import IOBase

from lib import State, Try, Invert, InstallException, UninstallException, DetectException



class Runnable(ABC):
    @abstractmethod
    def run(self) -> any:
        """
        Runs the Programm and returns something.
        """
        pass


class Shell(Runnable):
    """
    Can build and run shell commands.
    """
    def __init__(self, cmd: str):
        self.cmd = cmd

    def __repr__(self) -> str:
        return f"<Shell '{self.cmd:5}'>"

    def pipe(self, cmd: str) -> Shell:
        self.cmd += f" | {cmd}"
        return self

    def stdout(self, target: str) -> Shell:
        cmd = self.cmd + f" 1>{target}"
        return self

    def stderr(self, target: str) -> Shell:
        cmd = self.cmd + f" 2>{target}"
        return self

    def _get_process_owner_username(self) -> str:
        owner = os.getuid()
        pw_entry = pwd.getpwuid(owner)
        return pw_entry.pw_name

    def run(self, user: str = None, cwd: str = None, sudo: bool = False) -> subprocess.CompletedProcess:
        cmd = "sudo " + self.cmd if sudo else self.cmd
        cmd = os.path.expanduser(os.path.expandvars(cmd))
        user = user if user else self._get_process_owner_username()
        cwd = cwd if cwd else os.getcwd()
        print(f"{user}@{cwd} {cmd}")
        return subprocess.run(
                cmd,
                capture_output=True, 
                cwd=cwd, 
                user=user, 
                shell=True,
            )



class Command(State):
    """
    State that reaches his target State by running different Shell runnables.
    """

    def __init__(self, install: Shell, uninstall: Shell, detect: Shell):
        """
        install: Shell script to install target
        uninstall: Shell script to uninstall target
        detect: Shell script to detect if target is installed. Must return code 0 if installed or > 0 if not installed.
        """
        self._install = install
        self._uninstall = uninstall
        self._detect = detect

    def install(self):
        r = self._install.run()
        if r.returncode == 0:
            return
        raise InstallException(f"failed to install '{self.archive}'. \nstderr: {r.stderr.decode()}")

    def uninstall(self):
        r = self._uninstall.run()
        if r.returncode == 0:
            return
        raise UninstallException(f"failed to uninstall '{self.archive}'. \nstderr: {r.stderr.decode()}")

    def detect(self):
        r = self._detect.run()
        return r.returncode == 0


# packet managers

class Dpkg(State):
    def _get_package_name_from_archive(self, archive) -> str:
        r = Shell(f"dpkg --info '{archive}'").pipe('grep Package:').run()
        output = r.stdout.decode()
        num_lines = output.count('\n')
        assert num_lines == 1, f"Could not determine package name from debian archive '{archive}'."
        return output.split(": ")[1].strip()

    def __init__(self, archive: str):
        """
        archive: debian archive file (usually matched by *.deb)
        """
        self.archive = archive

    def install(self):
        assert os.path.isfile(archive), f"archive must be a file, got '{archive}'."
        r = Shell(f"dpkg --install '{self.archive}'").run(sudo=True)
        if r.returncode == 0:
            return
        raise InstallException(f"failed to install '{self.archive}'. \nstderr: {r.stderr.decode()}")

    def uninstall(self):
        assert os.path.isfile(archive), f"no debian archive found, got '{archive}'."
        package = self._get_package_name_from_archive(archive)

        r = Shell(f"dpkg --remove '{package}'").run(sudo=True)
        if r.returncode == 0:
            return
        raise UninstallException(f"failed to uninstall '{self.archive}'. \nstderr: {r.stderr.decode()}")

    def detect(self):
        r = Shell(f"dpkg --status '{self.package}'").run()
        return r.returncode == 0


class Apt(State):
    def __init__(self, package: str):
        """
        package: apt package name
        """
        self.package = package

    def install(self):
        r = Shell(f"apt install '{self.package}'").run(sudo=True)
        if r.returncode == 0:
            return
        raise InstallException(f"failed to install '{self.package}'. \nstderr: {r.stderr.decode()}")

    def uninstall(self):
        r = Shell(f"apt remove '{self.package}'").run(sudo=True)
        if r.returncode == 0:
            return
        raise UninstallException(f"failed to uninstall '{self.package}'. \nstderr: {r.stderr.decode()}")

    def detect(self) -> bool:
        r = Shell(f"dpkg --status '{self.package}'").run()
        return r.returncode == 0


class Snap(State):
    def __init__(self, package: str, classic: bool = False):
        """
        package: snap package name
        classic: install snap as classic snap
        """
        self.package = package
        self.classic = classic

    def install(self):
        r = Shell(f"snap install {'--classic' if self.classic else ''} '{self.package}'").run(sudo=True)
        if r.returncode == 0:
            return
        raise InstallException(f"failed to install '{self.package}'. \nstderr: {r.stderr.decode()}")

    def uninstall(self):
        r = Shell(f"snap remove '{self.package}'").run(sudo=True)
        if r.returncode == 0:
            return
        raise UninstallException(f"failed to uninstall '{self.package}'. \nstderr: {r.stderr.decode()}")

    def detect(self) -> bool:
        r = Shell(f"snap list '{self.package}'").run()
        return r.returncode == 0
        

class Flatpak(State):
    def __init__(self, package: str, system: bool = False):
        """
        package: name of flatpak package
        system: install package for entire system instead of only for current user
        """
        self.package = package
        self.system = '--system' if system else '--user'

    def install(self):
        r = Shell(f"flatpak install '{self.package}' -y {self.system}").run()
        if r.returncode == 0:
            return
        raise InstallException(f"failed to install '{self.package}'. \nstderr: {r.stderr.decode()}")

    def uninstall(self):
        r = Shell(f"flatpak uninstall '{self.package}' -y").run()
        if r.returncode == 0:
            return
        raise UninstallException(f"failed to uninstall '{self.package}'. \nstderr: {r.stderr.decode()}")

    def detect(self) -> bool:
        r = Shell(f"flatpak info '{self.package}'").run()
        return r.returncode == 0

# TODO test all below

class AddAptRepository(State):
    def __init__(self, ppa: str):
        """
        ppa: url to apt repository
        """
        self.ppa = ppa

    def install(self):
        # add ppa
        r = Shell(f"add-apt-repository '{self.ppa}' -y").run(sudo=True)
        if r.returncode != 0:
            raise InstallException(f"failed to add repository '{self.ppa}'. \nstderr: {r.stderr.decode()}")

    def uninstall(self):
        r = Shell(f"add-apt-repository --remove '{self.ppa}' -y").run(sudo=True)
        if r.returncode == 0:
            return
        raise UninstallException(f"failed to remove repository '{self.ppa}'. \nstderr: {r.stderr.decode()}")

    def detect(self) -> bool:
        r = Shell(f"add-apt-repository --list").pipe(f"grep '{self.ppa}'").run()
        output = r.stdout.decode()
        num_lines = output.count('\n')
        return num_lines > 0


class AddFlatpakRemote(State):
    def __init__(self, name: str, url: str, system: bool = False):
        self.name = name
        self.url = url
        self.system = 'system' if system else 'user'

    def install(self):
        r = Shell(f"sudo flatpak remote-add '{self.name}' '{self.url}'").run()
        if r.returncode != 0:
            raise InstallException(f"failed to install repository '{self.url}'. \nstderr: {r.stderr.decode()}")
        return


    def uninstall(self):
        r = Shell(f"sudo flatpak remote-delete '{self.name}'").run()
        if r.returncode != 0:
            raise UninstallException(f"failed to uninstall repository '{self.url}'. \nstderr: {r.stderr.decode()}")
        return


    def detect(self) -> bool:
        r = Shell("flatpak remotes --columns=name,options").pipe(f"grep '{self.name}.*{self.system}'").run()
        output = r.stdout.decode()
        num_lines = output.count('\n')
        return num_lines > 0


class Pip(State):
    def __init__(self, name: str):
        self.name = name

    def install(self):
        r = Shell(f"pip install '{self.name}'").run()
        if r.returncode != 0:
            raise InstallException(f"failed to install repository '{self.name}'. \nstderr: {r.stderr.decode()}")
        return


    def uninstall(self):
        r = Shell(f"pip uninstall '{self.name}' -y").run()
        if r.returncode != 0:
            raise UninstallException(f"failed to uninstall package '{self.name}'. \nstderr: {r.stderr.decode()}")
        return


    def detect(self) -> bool:
        r = Shell("pip list").pipe(f"grep '^{self.name}\s{2,}'").run()
        output = r.stdout.decode()
        num_lines = output.count('\n')
        return num_lines > 0


class GitClone(State):
    def __init__(self, url: str, path: str):
        """
        url: git repository url
        path: target path for repository
        """
        self.url = url
        self.path = path
        assert not os.path.isdir(path), f"can't clone git repository '{self.url}' to '{self.path}' since this directory already exists."

    def install(self):
        r = Shell(f"git clone --depth 1 '{self.url}' '{self.path}'").run()
        if r.returncode != 0:
            raise InstallException(f"failed to clone repository '{self.url}' to '{self.path}'.\n{r.stderr.decode()}")

    def uninstall(self):
        r = Shell(f"rm -rf '{self.path}'").run()
        if r.returncode != 0:
            raise UninstallException(f"failed to remove repository at '{self.path}'.\n{r.stderr.decode()}")

    def detect(self) -> bool:
        git_dir = os.path.join(self.path, '.git')
        return os.path.isdir(git_dir)

