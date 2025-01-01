# to be executed in root dir of the repo, otherwise imports break
from lib import *
from unix import *

if __name__ == '__main__':
    Chain(
        Print("# install discord via flathub"),
        Chain(
            Apt('flatpak'),
            AddFlatpakRemote('flathub', 'https://dl.flathub.org/repo/flathub.flatpakrepo'),
            Flatpak('com.discordapp.Discord'),
        ),

        Print("# install pandoc binary"),
        From(
            Command(
                Shell('wget https://github.com/jgm/pandoc/releases/download/3.6.1/pandoc-3.6.1-1-amd64.deb -qO /tmp/pandoc.deb'),
                Shell('rm /tmp/pandoc.deb'),
                Shell('test -f /tmp/pandoc.deb'),
            ),
            Dpkg('pandoc', '/tmp/pandoc.deb'), # requires root
        ),
    ).ensure_installed()
