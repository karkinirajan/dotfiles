# ==================================
# Basic Configuration
# ==================================
export ZSH="$HOME/.oh-my-zsh"       # Oh My Zsh installation directory
ZSH_THEME="agnoster"           # Theme for Oh My Zsh

# Display scaling for HiDPI screens
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_SCALE_FACTOR=1.5
export GDK_SCALE=2
export GDK_DPI_SCALE=0.5

# Terminal sizing alias
alias tsize="terminator -geometry 2000x1200+0+0"  

# ==================================
# Plugin Configuration
# ==================================
plugins=(
  git
  sudo          # Adds sudo prefix with ESC+ESC
  web-search    # Search web from command line
  zsh-autosuggestions  # Fish-like suggestions
  zsh-syntax-highlighting  # Syntax highlighting
  fzf           # Fuzzy finder
  history       # Better history management
)

source $ZSH/oh-my-zsh.sh            # Initialize Oh My Zsh
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh  # Fuzzy finder integration

# Enable Zsh syntax highlighting
if [ -f /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]; then
  source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
fi

# ==================================
# Key Bindings
# ==================================
# Enhanced history search with menu
autoload -Uz history-beginning-search-menu
zle -N history-beginning-search-menu
bindkey '^X^X' history-beginning-search-menu

# Enable case-insensitive tab completion
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

# Enable better history behavior
HISTSIZE=5000
SAVEHIST=10000
HISTFILE=~/.zsh_history
setopt APPEND_HISTORY
setopt SHARE_HISTORY
setopt HIST_IGNORE_ALL_DUPS

# ==================================
# System Utilities
# ==================================
# Package Management (APT)
alias update='sudo apt update && sudo apt list --upgradable' # Refresh package lists and show upgrades
alias upgrade='sudo apt upgrade -y'        # Apply updates
alias install='sudo apt install -y'        # Install packages
alias remove='sudo apt remove -y'          # Remove packages
alias purge='sudo apt purge -y'            # Remove with configs
alias autoremove='sudo apt autoremove -y'  # Remove unused dependencies
alias clean='sudo apt clean'               # Clean package cache
alias search-pkg='apt search'              # Search packages
alias show-pkg='apt show'                  # Show package details

# System Monitoring
alias df='df -h'              # Human-readable disk space
alias free='free -m'          # Show memory in MB
alias pstat='systemctl status'  # Service status check
alias top='htop'              # Use htop if installed

# File Operations
alias cp='cp -iv'            # Interactive copy with verification
alias mv='mv -iv'            # Interactive move
alias rm='rm -Iv'            # Interactive remove
alias ls='ls --color=auto'   # Colorized listing
alias ll='ls -alh'           # Detailed list with human sizes
alias cl='clear'             # Clear screen

# Directory Navigation
mkcd() { mkdir -p "$1" && cd "$1"; }  # Create and enter directory
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# ==================================
# Development Tools
# ==================================
# Git Aliases
alias ga='git add'
alias gaa='git add .'
alias gcm='git commit -m'
alias gd='git diff'
alias gi='git init'
alias gl='git log --oneline --graph --decorate'
alias gcl="git clone"
alias gpl='git pull'
alias gps='git push'
alias gpsh='git pull && git push'
alias gss='git status -s'
alias gacm="git add . && git commit -m"

# Python Development
alias venv='source ./venv/bin/activate'  # Virtual environment
alias runserver='python manage.py runserver'
alias makemigrations='python manage.py makemigrations'
alias migrate='python manage.py migrate'
alias createsuperuser='python manage.py createsuperuser'
alias collectstatic='python manage.py collectstatic'

# JavaScript/Node.js
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

alias nr='npm run'
alias ni='npm install'
alias ns='npm start'

# Editors
alias c='code .'  # VS Code
alias n='nano'    # Nano editor

# ==================================
# Network & Security
# ==================================
alias myip='curl ifconfig.me'       # Public IP address
alias ports='netstat -tulanp'       # Active listening ports
alias sshconfig='nano ~/.ssh/config'  # SSH configuration

# ==================================
# Custom Functions
# ==================================
# Show recent APT history
apt-history() {
  case "$1" in
    install)
      zgrep 'install ' /var/log/apt/history.log
      ;;
    upgrade|remove)
      zgrep "$1" /var/log/apt/history.log
      ;;
    *)
      echo "Usage: apt-history (install|upgrade|remove)"
      ;;
  esac
}

# Quick search function for the command history
hgrep() {
  history | grep "$1"
}

# Extract function for tar, zip, etc.
extract() {
  if [ -f "$1" ]; then
    case "$1" in
      *.tar.bz2) tar xjf "$1" ;;
      *.tar.gz) tar xzf "$1" ;;
      *.bz2) bunzip2 "$1" ;;
      *.rar) unrar x "$1" ;;
      *.gz) gunzip "$1" ;;
      *.tar) tar xf "$1" ;;
      *.tbz2) tar xjf "$1" ;;
      *.tgz) tar xzf "$1" ;;
      *.zip) unzip "$1" ;;
      *.7z) 7z x "$1" ;;
      *) echo "'$1' cannot be extracted via extract()" ;;
    esac
  else
    echo "'$1' is not a valid file"
  fi
}

# ==================================
# Final Initializations
# ==================================
# Enable Starship for a better prompt
if command -v starship &> /dev/null; then
  eval "$(starship init zsh)"
fi
