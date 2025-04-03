# to be executed in root dir of the repo, otherwise imports break
from lib import *
from unix import *

if __name__ == '__main__':
    # In this example we store the entire configuration in a single Chain object.
    # A Chain contains other States and allows to call methods like ensure_installed on all of them.
    Chain(
        Print("# install flatpak, add flathub repository and install discord"),
        # This operation can easily configured using a sequence of actions
        # Chain is not necessary here, but it allows us to group the following States together.
        Chain(
            # Utility class for installing an apt repository.
            Apt('flatpak'),
            # Utility class for installing a Flatpak repository.
            AddFlatpakRemote('flathub', 'https://dl.flathub.org/repo/flathub.flatpakrepo'),
            # Utility class for installing a flatpak.
            Flatpak('com.discordapp.Discord'),
        ),

        Print("# download pandoc debain file from github, install pandoc binary using dpkg and finally remove the debain file"),
        # This operation is quiet complex and we have to compose it.
        # First we note, that the debain file is removed after installation finished.
        # The utility class From installs a later removed dependency State necessary to install the given target State.
        From(
            # There is no utility class to download binaries from github, therefore we have to improvise by using the Command State.
            # The Command State allows us to make shell commands indempotent by defining actions install, detect and uninstall. 
            dependency=Command(
                install=Shell('wget https://github.com/jgm/pandoc/releases/download/3.6.1/pandoc-3.6.1-1-amd64.deb -qO /tmp/pandoc.deb'),
                uninstall=Shell('rm /tmp/pandoc.deb'),
                detect=Shell('test -f /tmp/pandoc.deb'),
            ),
            # A utility for Dpkg already exists and we use it here as target State.
            # Notice: here we can access the previously downloaded file '/tmp/pandoc.deb'.
            target=Dpkg('pandoc', '/tmp/pandoc.deb'), # Dpgk always requires root
        ),
    ).ensure_installed() # finally we call ensure_installed once on the root of the defined tree.
