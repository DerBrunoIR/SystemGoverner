> [!Warning]
> This project has no stable release yet and is not fully tested.

# What

We are proposing a library to configure your system in a declarative and [idempotent](https://en.wikipedia.org/wiki/Idempotence) fashion using Python.
Idempotency means, the library is able to detect if parts of the configuration are already installed or already uninstalled and is therefore able to skip those, reducing running time for small changes dramatically.

This library differentiates itself from the well known library and tool ansible in two ways:
- Python instead of YAML is used for configuration, allowing more flexibility in configurations.
- A simple Interface can be used for the definition and composition of states.

Additionally, there are some higher-order utility classes for more convenient configuration and some untested States for Ubuntu systems.


# Concepts

A **State** is any change you could do to a system that fulfills the following conditions:
- It can be *installed* by performing a sequence of actions.
- It must be *detectable* if the state is currently installed or not.
- It can be *uninstalled* by performing a sequence of actions.

A **higher-order State** is any State that operates on other States, chosen by the user.

# Example Usage

`example.py`:
```python
# imports omitted

if __name__ == '__main__':
    # In this example, we store the entire configuration in a single Chain object.
    # A Chain contains other States and allows calling methods like ensure_installed on all of them.
    Chain(
        Print("# install flatpak, add flathub repository and install discord"),
        # This operation can be configured using a sequence of actions
        # Chain is not necessary here, but it allows us to group the following States together.
        Chain(
            # Utility class for installing an apt repository.
            Apt('flatpak'),
            # Utility class for installing a Flatpak repository.
            AddFlatpakRemote('flathub', 'https://dl.flathub.org/repo/flathub.flatpakrepo'),
            # Utility class for installing a flatpak.
            Flatpak('com.discordapp.Discord'),
        ),

        Print("# download the Pandoc Debian file from GitHub, install Pandoc binary using dpkg, and finally remove the Debian file"),
        # This operation is quite complex, and we have to compose it.
        # First, we note, that the Debian file is removed after installation is finished.
        # The utility class From installs a later removed dependency State necessary to install the given target State.
        From(
            # There is no utility class to download binaries from GitHub; therefore, we have to improvise by using the Command State.
            # The Command State allows us to make shell commands idempotent by defining how to install, detect and uninstall them. 
            dependency=Command(
                install=Shell('wget https://github.com/jgm/pandoc/releases/download/3.6.1/pandoc-3.6.1-1-amd64.deb -qO /tmp/pandoc.deb'),
                uninstall=Shell('rm /tmp/pandoc.deb'),
                detect=Shell('test -f /tmp/pandoc.deb'),
            ),
            # A utility for global dpkg installations already exists, and we use it here as target State.
            # Notice: Here we can access the previously downloaded file '/tmp/pandoc.deb'.
            # For simplicity we skip all signature checks.
            target=Dpkg('pandoc', '/tmp/pandoc.deb'), # global installation requires ROOT
            # After target is installed '/tmp/pandoc.deb' will be deleted.
        ),
    ).ensure_installed() # Finally, we call ensure_installed once on the root of the defined tree.
```
Debug output from me, sadly displayed without colors here, together with explanations notated as `// annotation`:
```plain
# install flatpak, add flathub repository and install discord
user@~ dpkg --status 'flatpak' // flatpak is already installed
user@~ flatpak remotes --columns=name,options | grep 'flathub.*user' // flathub is already available
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

In the example, `From` checks twice if Pandoc is indeed installed. 
Higher-order utility classes, like `From`, can not know what actions States, like `dependency` and `target`, actually perform. 
For example a bad custom State could already install the `target` State and installing it twice could corrupt the existing installation.
Therefore, we carefully double-check.

A larger and less documented example can be found in `./my_ubuntu.py`.

# TODO

System configuration is difficult to test without writing some kind of mock.
Some time in the future, I will maybe investigate writing tests.
Until then, code might break.

Package the library.

Document Ubuntu utilities.

# Security

The Ubuntu utils are made for trusted input only, since they execute shell commands.

# Class Overview

- `State` Base class for idempotent state changes on the system

   **Any class** that implements the following interface and semantics can be used by all higher order utility classes. 
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
    - `From`: Temporally install dependency state required for installing the target state
    - `Breakpoint`: Enters a breakpoint before accessing the encapsulated state.
    - `Print`: just prints a message, has no encapsulated state
- Classes for **changing Ubuntu systems**:
    - `Command`: A state described by shell commands for installation, uninstallation and detection
    - `Dpkg`: State to install Debian packages from an archive
    - `Apt`: State to install apt packages
    - `Snap`: State to install snap packages
    - `Flatpak`: State to install Flatpak packages 
    - `Pip`: State to install pip packages
    - `GitClone`: State to clone git repositories
    - `AddAptRepository`: State to add apt repositories
    - `AddFlatpakRemote`: State to add flatpak remotes
- Helper classes that don't implement the State interface:
    - `Runnable`: Interface for something that can be `run`
    - `Shell`: Class for running shell commands

