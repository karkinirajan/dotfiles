# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# ==================================
# 🚀 Basic Configuration
# ==================================
export ZSH="$HOME/.oh-my-zsh"       # Oh My Zsh installation directory
ZSH_THEME="powerlevel10k/powerlevel10k"   # Theme for Oh My Zsh

# ==================================
# 🔌 Plugin Configuration
# ==================================
plugins=(
  git
  sudo          # Press ESC+ESC to prefix command with sudo
  web-search    # Search web from command line
  zsh-autosuggestions  # Fish-like autosuggestions
  zsh-syntax-highlighting  # Syntax highlighting
  fzf           # Fuzzy finder
  history       # Better history management
)

source $ZSH/oh-my-zsh.sh            # Initialize Oh My Zsh
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh  # Fuzzy finder integration

# Enable Zsh syntax highlighting (adjusted for Arch/Manjaro path)
if [ -f /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]; then
  source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
fi

# ==================================
# ⌨️ Key Bindings & History
# ==================================
# Enhanced history search with menu
autoload -Uz history-beginning-search-menu
zle -N history-beginning-search-menu
bindkey '^X^X' history-beginning-search-menu

# Case-insensitive tab completion
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

# Optimized history settings
HISTSIZE=10000
SAVEHIST=20000
HISTFILE=~/.zsh_history
setopt APPEND_HISTORY      # Append to history file instead of overwriting
setopt SHARE_HISTORY       # Share history between terminals
setopt HIST_IGNORE_ALL_DUPS  # Remove duplicate commands from history
setopt HIST_VERIFY         # Require confirmation before running a history command
setopt INC_APPEND_HISTORY  # Write history incrementally

# ==================================
# 🛠️ System Utilities
# ==================================
# Package Management (Pacman for Arch/Manjaro)
alias update='sudo pacman -Syu'          # Full system update
alias upgrade='sudo pacman -Syu'         # Same as update (consistency with previous setup)
alias install='sudo pacman -S'           # Install packages
alias remove='sudo pacman -R'            # Remove packages
alias purge='sudo pacman -Rns'           # Remove with dependencies and configs
alias autoremove='sudo pacman -Rns $(pacman -Qdtq)'  # Remove orphaned packages
alias clean='sudo pacman -Sc'            # Clean package cache
alias search-pkg='pacman -Ss'            # Search packages
alias show-pkg='pacman -Qi'              # Show installed package details

# Optional: Yay (AUR helper) aliases if installed
if command -v yay &> /dev/null; then
  alias aur-update='yay -Syu'            # Update including AUR packages
  alias aur-install='yay -S'             # Install from AUR or repos
  alias aur-search='yay -Ss'             # Search AUR and repos
fi

# System Monitoring
alias df='df -h'              # Human-readable disk space
alias free='free -m'          # Show memory in MB
alias pstat='systemctl status'  # Service status check
alias top='htop'              # Use htop if installed
alias psu='ps aux --sort=-%cpu | head -10'  # Show top 10 CPU processes
alias psm='ps aux --sort=-%mem | head -10'  # Show top 10 memory processes
alias inuse='lsof +D . | awk "{print \$2}" | sort -u | xargs ps u'  # Show processes using a directory

# File Operations
alias cp='cp -iv'            # Interactive copy with verification
alias mv='mv -iv'            # Interactive move
alias rm='rm -Iv'            # Interactive remove (ask before deleting multiple files)
alias ls='ls --color=auto'   # Colorized listing
alias ll='ls -alh'           # Detailed list with human sizes
alias cl='clear'             # Clear screen

# Directory Navigation
mkcd() { mkdir -p "$1" && cd "$1"; }  # Create and enter directory
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# ==================================
# 👨‍💻 Development Tools
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
# 🌐 Network & Security
# ==================================
alias myip='curl ifconfig.me'       # Public IP address
alias ports='netstat -tulanp'       # Active listening ports
alias sshconfig='nano ~/.ssh/config'  # SSH configuration

# ==================================
# 🔧 Custom Functions
# ==================================
# Show recent Pacman history (replacing apt-history)
pacman-history() {
  if [ -f /var/log/pacman.log ]; then
    case "$1" in
      install)
        grep "installed" /var/log/pacman.log
        ;;
      upgrade)
        grep "upgraded" /var/log/pacman.log
        ;;
      remove)
        grep "removed" /var/log/pacman.log
        ;;
      *)
        echo "Usage: pacman-history (install|upgrade|remove)"
        ;;
    esac
  else
    echo "Pacman log not found at /var/log/pacman.log"
  fi
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
# ✨ Final Initializations
# ==================================
# Enable Starship for a better prompt
if command -v starship &> /dev/null; then
  eval "$(starship init zsh)"
fi

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
