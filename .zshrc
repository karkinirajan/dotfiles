# ==================================
# Powerlevel10k Instant Prompt
# ==================================
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# ==================================
# Basic Configuration
# ==================================
export ZSH="/home/kneeraazon/.oh-my-zsh"
USE_POWERLINE="true"
HOST_NAME=kneeraazon

# ==================================
# Plugin Configuration
# ==================================
plugins=(
  git
  rake
  web-search
  zsh-autosuggestions
)

# Source configurations
source $ZSH/oh-my-zsh.sh
source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# ==================================
# Key Bindings
# ==================================
autoload -Uz history-beginning-search-menu
zle -N history-beginning-search-menu
bindkey '^X^X' history-beginning-search-menu

# ==================================
# System Utilities
# ==================================
# Directory Operations
function mkcd() {
    mkdir $1 && cd $1
}

alias cp="cp -i"                    # Confirm before overwriting
alias df='df -h'                    # Human-readable sizes
alias free='free -m'               # Show sizes in MB
alias more=less
alias np='nano -w PKGBUILD'

# Navigation
alias l="ls"                       # List files
alias ll="ls -la"                  # Detailed list
alias cl="clear"
alias cd..='cd ..'

# System Management
alias watchers="echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p"
alias update="sudo pacman -Syyy"
alias install="sudo pacman -Syu"
alias ether="sudo modprobe r8169"

# ==================================
# Development Tools
# ==================================
# VS Code
alias c='code .'
alias a='code .'

# Node.js / NPM
alias ns='npm start'
alias nr='npm run'
alias nis='npm i -S'
alias nrd="npm run develop"

# React
alias create="npx create-react-app"
alias gd="gatsby develop"

# Django
alias runserver="python manage.py runserver"
alias makemigrations="python manage.py makemigrations"
alias migrate="python manage.py migrate"
alias collectstatic="python manage.py collectstatic"
alias createsuperuser="python manage.py createsuperuser"

# Database
alias postgres="sudo -u postgres psql"

# Virtual Environment
alias venv="source ~/venv/bin/activate"

# ==================================
# Git Aliases
# ==================================
alias ga='git add'
alias gaa='git add .'
alias gaaa='git add -A'
alias gc='git commit'
alias gcm='git commit -m'
alias gd='git diff'
alias gi='git init'
alias gl='git log'
alias gc="git clone"
alias gp='git pull'
alias gpsh='git pull && git push'
alias gss='git status -s'
alias gacm="git add . && git commit -m"
alias gs='echo ""; echo "*********************************************"; echo -e "   DO NOT FORGET TO PULL BEFORE COMMITTING"; echo "*********************************************"; echo ""; git status'

# ==================================
# SSH Configuration
# ==================================
alias skpb="cat ~/.ssh/id_rsa.pub"
alias skpv="cat ~/.ssh/id_rsa"

# ==================================
# Theme Configuration
# ==================================
source ~/powerlevel10k/powerlevel10k.zsh-theme
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# ==================================
# NVM Configuration
# ==================================
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# ~/.zshrc

eval "$(starship init zsh)"