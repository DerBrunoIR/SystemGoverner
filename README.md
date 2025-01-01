This python library contains utils to configure your system in a declarative and [indempotent](https://en.wikipedia.org/wiki/Idempotence) fashion.
Those utils are easy to extend and modify for your needs.


# Example Usage

```python
    # tobe executed in root dir of the repo
    from lib import *
    from unix import *

    if __name__ == '__main__':
        Chain(
            Print('# install discord'),
            Chain(
                Apt('flatpak'),
                AddFlatpakRemote('flathub', 'https://dl.flathub.org/repo/flathub.flatpakrepo'),
                Flatpak('com.discordapp.Discord'),
            ),

            Print("# setup nvim"),
            Chain(
                Print("## install nvim"),
                Command(
                    install=Shell('sudo wget https://github.com/neovim/neovim/releases/download/v0.10.3/nvim.appimage -O /usr/local/bin/nvim'),
                    uninstall=Shell('sudo rm /usr/local/bin/nvim'),
                    detect=Shell('test -f /usr/local/bin/nvim'),
                    ),
                Print("## clone nvim configuration"),
                GitClone('git@github.com:DerBrunoIR/NeoVimConfig.git', '~/.config/nvim'),
            ),

            Print("# install pandoc"),
            From(
                Command(
                    Shell('wget https://github.com/jgm/pandoc/releases/download/3.6.1/pandoc-3.6.1-1-amd64.deb -qO /tmp/pandoc.deb'),
                    Shell('rm /tmp/pandoc.deb'),
                    Shell('test -f /tmp/pandoc.deb'),
                ),
                Dpkg('pandoc', '/tmp/pandoc.deb'),
            ),
        ).ensure_installed()
```

A large example can be found in `./my_ubuntu.py`.


# Documentation

- `State` Base class for idempotent state changes on the system

    This interface is used by all other utils:
    ```python
    class State(ABC):
        def install(self) -> None:
            """
            Installs target state on system. 
            Undefined behavior if target State is already installed.
            """
            pass

        def uninstall(self) -> None:
            """
            Uninstalls target state from system.
            Undefined behavior if target State is already uninstalled.
            """
            pass

        def detect(self) -> bool:
            """
            Returns True if the target state is already installed otherwise False.
            """
            pass
    ```
    

The following classes **encapsulate** other states.

- `Chain`: chain multiple states together.
- `Try`: Ignore exceptions from encapsulated state. 
- `Invert`: Swap `install` and `uninstall` method.
- `From`: Temporally install dependency state to install target state.
- `Breakpoint`: Enters a breakpoint before accessing encapsulated state.
- `Print`: just prints a message, has no encapsulated state.


The following classes are useful for **changing** Ubuntu systems:

- `Command`: A state described by shell commands for installation, uninstallation and detection.
- `Dpkg`: State to install Debian packages from an archive.
- `Apt`: State to install apt packages.
- `Snap`: State to install snap packages.
- `Flatpak`: State for install flatpak packages. 
- `Pip`: State for adding pip packages.
- `GitClone`: State for cloning git repositories.
- `AddAptRepository`: State for adding apt repositories.
- `AddFlatpakRemote`: State for adding flatpak remotes.

- `Runnable`: Interface for something that can be `run`.
- `Shell`: Class for running shell commands.

