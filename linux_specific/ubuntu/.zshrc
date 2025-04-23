# ==================================
# 🚀 Zsh Configuration for Ubuntu
# ==================================
# This configuration file is tailored for Zsh on Ubuntu,
# aiming for efficiency and advanced user features.

# Oh My Zsh installation directory
export ZSH="$HOME/.oh-my-zsh"

# Set the Oh My Zsh theme. Choose a minimal or powerline theme
# for a more advanced look, or keep default. Starship is recommended
# later in the file for a highly customizable prompt.
ZSH_THEME="robbyrussell" # You can change this, e.g., "agnoster", "powerlevel10k", or "" for a minimal prompt if using Starship.

# ==================================
# 🔌 Plugin Configuration (Oh My Zsh)
# ==================================
# Define which Oh My Zsh plugins to load. Install plugins
# by cloning them into ~/.oh-my-zsh/custom/plugins/.
plugins=(
  git                  # Adds many useful git aliases and functions
  # sudo                 # Press ESC+ESC to prefix the current command with sudo.
                         # Advanced users might prefer typing sudo manually. Uncomment if desired.
  # web-search           # Search web from command line (e.g., zsh google search <query>).
                         # Niche plugin, advanced users might prefer dedicated tools or browser. Uncomment if desired.
  zsh-autosuggestions  # Suggests commands based on history as you type (needs installation)
                         # Install: git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
  zsh-syntax-highlighting # Highlights commands as you type (needs installation)
                         # Install: git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
  fzf                    # Integrates the fuzzy finder (fzf must be installed separately)
                         # fzf provides fuzzy search for history, files, etc.
  history                # Adds history command aliases and functions (often default)
  # Add other plugins here, e.g., docker, kubectl, aws, vscode, etc.
)

# Initialize Oh My Zsh. This must be sourced AFTER plugins are defined.
source $ZSH/oh-my-zsh.sh

# Source fzf key bindings and completion if installed.
# This line assumes fzf was installed system-wide or via a method
# that places the sourcing file in your home directory.
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# Note: The manual sourcing of zsh-syntax-highlighting for Arch path
# is removed. Oh My Zsh handles sourcing plugins listed above
# if they are installed correctly in the custom plugins directory.


# ==================================
# ⌨️ Key Bindings & History
# ==================================
# Enhanced history search with menu. Bind to ^X^X (Ctrl+X, Ctrl+X).
# This shows a menu of history items matching the start of the line.
autoload -Uz history-beginning-search-menu
zle -N history-beginning-search-menu
bindkey '^X^X' history-beginning-search-menu

# Case-insensitive tab completion. Allows 'cd /hOmE' to complete correctly.
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

# Optimized history settings for long-term, shared history.
HISTSIZE=10000       # Maximum number of history entries stored in memory
SAVEHIST=20000       # Maximum number of history entries saved to the history file
HISTFILE=~/.zsh_history # Path to the history file

setopt APPEND_HISTORY       # Append new history lines to the file instead of overwriting it
setopt SHARE_HISTORY        # Share history across all Zsh sessions
setopt HIST_IGNORE_ALL_DUPS # Remove duplicate commands from history
setopt HIST_VERIFY          # Show command from history before executing it (hit Enter again to run) - can be annoying, comment out if not desired.
setopt INC_APPEND_HISTORY   # Write history to the file immediately after each command is executed

# ==================================
# 🛠️ System Utilities (Ubuntu - apt)
# ==================================
# Package Management Aliases using apt for Ubuntu.
alias update='sudo apt update && sudo apt upgrade -y' # Update package lists and upgrade installed packages non-interactively
alias upgrade='sudo apt upgrade -y'                   # Upgrade installed packages non-interactively
alias install='sudo apt install'                      # Install new packages
alias remove='sudo apt remove'                        # Remove packages
alias purge='sudo apt purge'                          # Remove packages and their configuration files
alias autoremove='sudo apt autoremove'                # Remove unused packages that were installed as dependencies
alias clean='sudo apt clean'                          # Clear out the local repository of retrieved package files
alias search-pkg='apt search'                         # Search for packages
alias show-pkg='apt show'                             # Show detailed information about a package

# Ubuntu doesn't use AUR or Yay. This section is removed.

# System Monitoring Aliases.
alias df='df -h'              # Show disk space in human-readable format
alias free='free -m'          # Show memory usage in MB
alias pstat='systemctl status'  # Check the status of a systemd service
alias top='htop'              # Use htop for process monitoring (install htop if you don't have it: sudo apt install htop)
alias psu='ps aux --sort=-%cpu | head -10'  # Show top 10 processes by CPU usage
alias psm='ps aux --sort=-%mem | head -10'  # Show top 10 processes by memory usage
alias inuse='lsof +D . | awk "{print \$2}" | sort -u | xargs ps u'  # Show processes using the current directory

# File Operations Aliases.
alias cp='cp -iv'            # Interactive copy with verbose output
alias mv='mv -iv'            # Interactive move with verbose output
alias rm='rm -i'             # Interactive remove (prompt before every removal). Use 'rm' directly for no prompt (advanced user preference).
alias ls='ls --color=auto'   # Colorized listing
alias ll='ls -alh'           # Detailed list with human-readable sizes
alias cl='clear'             # Clear the terminal screen

# Directory Navigation Shortcuts and Function.
mkcd() {                      # Function to create a directory and immediately change into it
  mkdir -p "$1" && cd "$1";
}
alias ..='cd ..'              # Go up one directory
alias ...='cd ../..'          # Go up two directories
alias ....='cd ../../..'      # Go up three directories
# alias -- -='cd -'           # Go to the previous directory (already a Zsh built-in shortcut)

# Networking utility aliases
alias myip='curl ifconfig.me' # Get your public IP address
alias ports='ss -tulpn'       # List active listening ports using the 'ss' utility (more modern than netstat)
alias ipa='ip a'              # Show network interface addresses using the 'ip' utility (more modern than ifconfig)

# ==================================
# 👨‍💻 Development Tools
# ==================================
# Common Git Aliases (Oh My Zsh git plugin provides many more)
alias ga='git add'
alias gaa='git add .'
alias gcm='git commit -m'
alias gd='git diff'
alias gi='git init'
alias gl='git log --oneline --graph --decorate' # Pretty git log graph
alias gcl="git clone"
alias gpl='git pull'
alias gps='git push'
alias gpsh='git pull && git push' # Pull and then push
alias gss='git status -s'         # Short git status
alias gacm="git add . && git commit -m" # Add all and commit with a message

# Python Development Aliases (Django-specific examples)
alias venv='source ./venv/bin/activate'  # Activate a Python virtual environment in ./venv
alias runserver='python manage.py runserver' # Run Django development server
alias makemigrations='python manage.py makemigrations' # Create Django database migrations
alias migrate='python manage.py migrate'  # Apply Django database migrations
alias createsuperuser='python manage.py createsuperuser' # Create a Django superuser
alias collectstatic='python manage.py collectstatic' # Collect static files in Django

# JavaScript/Node.js Setup (using NVM - Node Version Manager)
# This block sources NVM if it's installed according to its standard instructions.
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion" # This loads nvm bash_completion

# Common NPM Aliases
alias nr='npm run'
alias ni='npm install'
alias ns='npm start'

# Editor Aliases. Advanced users often prefer powerful editors.
alias c='code .'  # Open current directory in VS Code (install code from code.visualstudio.com)
alias nv='nvim'   # Alias for Neovim (install with: sudo apt install neovim)
alias v='vim'     # Alias for Vim (install with: sudo apt install vim)
# alias n='nano'  # Alias for Nano (simple editor, uncomment if preferred)
alias dotfiles='nv ~/.dotfiles' # Example: Edit your dotfiles using nvim (adjust path)
alias zshrc='nv ~/.zshrc'       # Edit this zshrc file quickly

# ==================================
# 🔧 Custom Functions
# ==================================
# Show recent apt package history (install, upgrade, remove)
# Reads the apt history log file.
apt-log-history() {
  # Check if the apt history log file exists
  if [ -f /var/log/apt/history.log ]; then
    # Use awk to format output, filtering by action keywords
    awk '/^(Commandline|Install:|Upgrade:|Remove:)/' /var/log/apt/history.log |
    # Further process to grep for specific actions
    case "$1" in
      install)
        grep -A 1 "Install:" /var/log/apt/history.log
        ;;
      upgrade)
        grep -A 1 "Upgrade:" /var/log/apt/history.log
        ;;
      remove)
        grep -A 1 "Remove:" /var/log/apt/history.log
        ;;
      *)
        echo "Usage: apt-log-history (install|upgrade|remove)"
        # Show last few entries by default if no argument given or argument is invalid
        # tail /var/log/apt/history.log
        ;;
    esac
  else
    echo "Apt history log not found at /var/log/apt/history.log"
  fi
}

# Quick search function for the command history using grep
hgrep() {
  history | grep "$1"
}

# Function to extract various archive types
extract() {
  if [ -f "$1" ]; then
    case "$1" in
      *.tar.bz2) tar xjf "$1" ;;
      *.tar.gz) tar xzf "$1" ;;
      *.bz2) bunzip2 "$1" ;;
      *.rar) unrar x "$1" ;; # Requires 'unrar-free' or 'unrar' package (sudo apt install unrar)
      *.gz) gunzip "$1" ;;
      *.tar) tar xf "$1" ;;
      *.tbz2) tar xjf "$1" ;;
      *.tgz) tar xzf "$1" ;;
      *.zip) unzip "$1" ;; # Requires 'unzip' package (sudo apt install unzip)
      *.7z) 7z x "$1" ;;   # Requires 'p7zip-full' package (sudo apt install p7zip-full)
      *) echo "'$1' cannot be extracted via extract()" ;;
    esac
  else
    echo "'$1' is not a valid file"
  fi
}

# ==================================
# ✨ Final Initializations
# ==================================
# Enable Starship for a highly customizable prompt.
# Install Starship first: https://starship.rs/guide/#🚀installation
# This block initializes Starship if the command is found.
if command -v starship &> /dev/null; then
  eval "$(starship init zsh)"
fi

# You might want to place other sourcing lines here, e.g., for specific
# tools or frameworks that require shell integration.
# source /opt/mytool/tool.sh