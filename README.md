# Prototype

This respository contains utils to configure your system in a declarative and [indempotent](https://en.wikipedia.org/wiki/Idempotence) fashion using python.

The main features is the convinience of python as configuration language and the simplicity of the only interface `State`.

# TODO

System configuration is difficult to test without much effort.
Some time in the future I will probably investigate writing tests.
Until then, most code is tested only manually by me.

# Example Usage

`example.py`:
```python
# to be executed in root dir of the repo, otherwise imports break
from lib import *
from unix import *

if __name__ == '__main__':
    Chain(
        Print("# install flatpak, add flathub repository and install discord"),
        Chain(
            Apt('flatpak'), 
            AddFlatpakRemote('flathub', 'https://dl.flathub.org/repo/flathub.flatpakrepo'),
            Flatpak('com.discordapp.Discord'),
        ),

        Print("# download pandnoc debain file, install pandoc binary using dpkg and finally remove the debain file"),
        From(
            dependency=Command(
                install=Shell('wget https://github.com/jgm/pandoc/releases/download/3.6.1/pandoc-3.6.1-1-amd64.deb -qO /tmp/pandoc.deb'),
                uninstall=Shell('rm /tmp/pandoc.deb'),
                detect=Shell('test -f /tmp/pandoc.deb'),
            ),
            target=Dpkg('pandoc', '/tmp/pandoc.deb'), # requires root
        ),
    ).ensure_installed()
```
Debug output, sadly only displayed without colors here, together with explanations notated as `// annotation`:
```plain
# install flatpak, add flathub repository and install discord
user@~ dpkg --status 'flatpak' // flatpak is already installed
user@~ flatpak remotes --columns=name,options | grep 'flathub.*user' // flathub is allready available
user@~ flatpak info 'com.discordapp.Discord'  // discord flatpak is already installed
# install pandoc binary
user@~ dpkg --status 'pandoc' // pandoc is not installed
user@~ test -f /tmp/pandoc.deb // pandoc debain file does not exist
user@~ wget https://github.com/jgm/pandoc/releases/download/3.6.1/pandoc-3.6.1-1-amd64.deb -qO /tmp/pandoc.deb // download debain file from url
user@~ dpkg --status 'pandoc' // pandoc is still not installed
user@~ sudo dpkg --install '/tmp/pandoc.deb' // install pandoc from debain file
user@~ test -f /tmp/pandoc.deb // check if debain file exists
user@~ rm /tmp/pandoc.deb // remove debian file
```

In the example, `From` checks twice if pandoc is indeed installed. 
Higher order utility classes, like `From`, can not know what actions States, like `dependency` and `target`, actually perform. 
Therfore we are carfull about all assumptions we take about given States and to not currupt any configuration, though resulting from strange configurations, we do multiple checks. 

A large example can be found in `./my_ubuntu.py`.

# Security

The Ubuntu utils are made for trusted input only, since they execute shell commands.

# Class Overview

- `State` Base class for idempotent state changes on the system

    The only important interface:
    ```python
    class State(ABC):
        """
        Abstraction for installing, detecting and uninstalling a target state from the system.
        """
        @abstractmethod
        def detect(self) -> bool:
            """
            Returns true if the target state is already installed false otherwise.
            """
            pass
    
        @abstractmethod
        def install(self) -> None:
            """
            Installs target state on system. 
            Undefined behavior if target State is already installed.
            """
            pass
    
        @abstractmethod
        def uninstall(self) -> None:
            """
            Uninstalls target state from system.
            Undefined behavior if target State is already uninstalled.
            """
            pass
    ```
    

- Classes **encapsulating** other states:
    - `Chain`: chain multiple states together
    - `Try`: Ignore exceptions from encapsulated state 
    - `Invert`: Swap `install` and `uninstall` method
    - `From`: Temporally install dependency state to install another target state
    - `Breakpoint`: Enters a breakpoint before accessing encapsulated state
    - `Print`: just prints a message, has no encapsulated state
- Classes for **changing Ubuntu systems**:
    - `Command`: A state described by shell commands for installation, uninstallation and detection
    - `Dpkg`: State to install Debian packages from an archive
    - `Apt`: State to install apt packages
    - `Snap`: State to install snap packages
    - `Flatpak`: State to install flatpak packages 
    - `Pip`: State to install pip packages
    - `GitClone`: State to clone git repositories
    - `AddAptRepository`: State to add apt repositories
    - `AddFlatpakRemote`: State to add flatpak remotes
- Helper classes that don't implement the State interface:
    - `Runnable`: Interface for something that can be `run`
    - `Shell`: Class for running shell commands

