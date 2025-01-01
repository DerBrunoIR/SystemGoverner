from lib import *
from unix import *



def main():
    Chain(
            # Apt packages
            Apt('docker-ce'),
            Apt('docker-ce-cli'),
            Apt('containerd.io'),
            Apt('docker-buildx-plugin'),
            Apt('docker-compose-plugin'),
            Apt('flatpak'),
            Apt('zsh'),
            Apt('jq'),
            Apt('git'),
            Apt('sed'),
            Apt('mawk'),
            Apt('grep'),
            Apt('tree'),
            Apt('nmap'),
            Apt('curl'),
            Apt('wget'),
            Apt('bat'),
            Apt('xclip'),
            Apt('tar'),
            Apt('zip'),
            Apt('autojump'),
            Apt('vim'),
            Apt('python3'),
            Apt('python3-pip'),
            Apt('python3-venv'),
            Apt('maven'),
            Apt('clang'),
            Apt('gdb'),
            Apt('evince'),
            Apt('ripgrep'),
            Apt('flatpak'),

            # Flatpak packages
            AddFlatpakRemote('flatpak', 'https://dl.flathub.org/repo/flathub.flatpakrepo'),
            Flatpak('com.google.Chrome'),
            Flatpak('com.discordapp.Discord'),
            Flatpak('com.spotify.Client'),
            Flatpak('org.mozilla.Thunderbird'),
            Flatpak('net.ankiweb.Anki'),
            Flatpak('org.kde.kdenlive'),
            Flatpak('com.github.jeromerobert.pdfarranger'),
            Flatpak('com.nextcloud.desktopclient.nextcloud'),
            Flatpak('org.onlyoffice.desktopeditors'),
            Flatpak('com.mattjakeman.ExtensionManager'),
            Flatpak('io.github.Qalculate'),

            # custom 
            # docker
            # nvim
    # nvim config
            # autojump
            # dotfiles
            # sdkman 
            # golang
            # ohmyzsh
            # starship prompt
            # nerd fonts
            # bat symlink

            # dpkg packages
            Dpkg(),
            # pandoc

            # snap packages
            Snap(),

            # python packages
              Pip('ipython'),
              Pip('ipdb'),
              Pip('grip'),
              Pip('docker'),
              Pip('neovim'),
              Pip('numpy'),
              Pip('pandas'),
            ).ensure_installed()

if __name__ == "__main__":
    main()

"""
---
- name: Initialize my personal ubuntu configuration
  hosts: localhost
  # remote_user: bruno

  vars:
    - golang_version: 1.20.1.linux-amd64
    - neovim_version: v0.10.1
    - neovim_config_repository: https://github.com/DerBrunoIR/nvim.git
    - dotfiles_repository: https://github.com/DerBrunoIR/dotfiles.git
    - shell_profile: ~/.setup
    - starship_preset: https://starship.rs/presets/toml/nerd-font-symbols.toml      

  tasks:

    - name: init bash profile
      shell:
        cmd: |
          echo "#/bin/bash" > {{ shell_profile }}
        creates: "{{ shell_profile }}"



    - name: add Docker GPG apt key
      apt_key:
        url: https://download.docker.com/linux/ubuntu/gpg
        state: present

    - name: add Docker apt repository
      apt_repository:
        repo: deb https://download.docker.com/linux/ubuntu focal stable
        state: present

    - name: add autojump to shell profile
      shell:
        echo "source /usr/share/autojump/autojump.sh" >> {{ shell_profile }}

    - name: create symlink cat for batcat 
      file:
        src: /bin/batcat
        dest: /bin/bat
        mode: a+r
        state: link


    - name: install sdkman
      shell:
        cmd: |
          curl -s "https://get.sdkman.io" | bash
          echo 'source "$HOME/.sdkman/bin/sdkman-init.sh"' >> {{ shell_profile }}
        creates: "~/.sdkman/bin/sdkman-init.sh"



    - name: install golang
      shell:
        cmd: |
          wget https://go.dev/dl/go{{ golang_version }}.tar.gz -O /tmp/go.tar.gz
          tar -C /usr/local -xzf /tmp/go.tar.gz
          rm /tmp/go.tar.gz
          echo "PATH=\$PATH:/usr/local/go/bin:~/go/bin" >> {{ shell_profile }}
      args:
        creates: /usr/local/go



    - name: install neovim
      shell:
        cmd: | 
          wget https://github.com/neovim/neovim/releases/download/{{ neovim_version }}/nvim.appimage -O /usr/local/bin/nvim
          chmod a+x /usr/local/bin/nvim
          echo "PATH=\$PATH:/usr/local/bin/nvim" >> {{ shell_profile }}
        creates: /usr/local/bin/nvim

    - name: install neovim configuration
      shell:
        cmd: |
          mkdir -p ~/.config/
          git clone {{ neovim_config_repository }} ~/.config/nvim
        creates: ~/.config/nvim



    - name: install dotfiles
      shell: 
        cmd: | 
          git clone {{ dotfiles_repository }} ~/dotfiles
          if [[ -x ./install ]]
            ~/dotfiles/install
        creates: ~/dotfiles



    - name: install oh my zsh
      shell:
        cmd: |
          sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"
          echo "source \$ZSH/oh-my-zsh.sh" > {{ shell_profile }}
        creates: ~/.oh-my-zsh

    - name: install nerd font
      shell:
        cmd: | 
          wget https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/JetBrainsMono.zip
          unzip JetBrainsMono.zip -d ~/.fonts
          rm JetBrainsMono.zip
          fc-cache -fv
        creates: ~/.fonts/JetBrainsMonoNLNerdFont-Regular.ttf

    - name: install starship prompt
      shell:
        cmd: |
          wget https://starship.rs/install.sh -O /tmp/install.sh;
          chmod u+x /tmp/install.sh
          /tmp/install.sh -y
          rm /tmp/install.sh
          wget {{ starship_preset }} -O ~/.config/starship.toml;
          echo "eval \"\$(starship init zsh)\"" >> {{ shell_profile }}
        creates: ~/.config/starship.toml



         

...
"""
