This python library contains utils to configure your system in a declarative and [indempotent]<https://en.wikipedia.org/wiki/Idempotence> fashion.
Those utils are easy to extend and modify for your needs.

Included are:

- `State` Base class for idempotent state changes on the system

    This interface is used by most other utils:
    ```python
    class State(ABC):
        def install(self) -> None:
            """
            Installs target state on system. 
            Undefined behaivior if target State is already installed.
            """
            pass

        def uninstall(self) -> None:
            """
            Uninstalls target state from system.
            Undefined behaivior if target State is already uninstalled.
            """
            pass

        def detect(self) -> bool:
            """
            Returns true if the target state is already installed.
            """
            pass
    ```
    
    The following classes encapsulate other states.
	- `Chain`: chain multiple states together.
	- `Try`: Ignore exceptions from encapsulated state. 
	- `Invert`: Swap `install` and `uninstall` method.
	- `From`: Temporally install dependency state to install target state.
	- `Breakpoint`: Enters a breakpoint before accessing encapsulated state.

	- `Print`: just prints a message, has no encapsulated state.

The file `unix.py` contains classes for UNIX command line utils:

- `Runnable`: Interface for runnable things.
    - `Shell`: A runnable shell command.

- `State` interface implemented by the following classes:
    - `Command`: A state described by shell commands for installation, uninstallation and detection.
    - `Dpkg`: State to install debian packages from an archive.
    - `Apt`: State to install apt packages.
    - `Snap`: State to install snap packages.
    - `Flatpak`: State for install flatpak packages. 
    - `Pip`: State for adding pip packages.
    - `GitClone`: State for cloning git repository.
    - `AddAptRepository`: State for adding an apt ppa.
    - `AddFlatpakRemote`: State for adding a flatpak remote.

# Example
```python
    if __name__ == '__main__':
        Chain(
            Print('# install discord'),
            Chain(
                Apt('flatpak'),
                AddFlatpakRemote('flathub', 'https://dl.flathub.org/repo/flathub.flatpakrepo'),
                Flatpak('com.discordapp.Discord'),

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
