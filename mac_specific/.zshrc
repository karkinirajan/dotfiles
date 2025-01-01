# ==================================
# PATH and Environment Configuration
# ==================================
export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH
export ZSH="$HOME/.oh-my-zsh"
export NVM_DIR="$HOME/.nvm"
export alias python="python3"

# ==================================
# Oh-My-Zsh Configuration
# ==================================
ZSH_THEME="robbyrussell"
plugins=(git zsh-autosuggestions)
source $ZSH/oh-my-zsh.sh
USE_POWERLINE="true"
HOST_NAME=kneeraazon

# ==================================
# File Operations
# ==================================
alias cp="cp -i"                    # Confirm before overwriting
alias df='df -h'                    # Human-readable sizes
alias free='free -m'               # Show sizes in MB
alias more=less
alias np='nano -w PKGBUILD'

# Directory Navigation
alias l="ls"                       # List files
alias ll="ls -al"                  # Detailed list with hidden files
alias cd..='cd ..'

# VS Code
alias c="open -a 'Visual Studio Code'"
alias code="open -a 'Visual Studio Code'"
alias a='code .'

# ==================================
# Development Tools
# ==================================
# Node.js / NPM
alias ns='npm start'
alias nr='npm run'
alias nis='npm i -S'

# Django
alias runserver="python manage.py runserver"
alias makemigrations="python manage.py makemigrations"
alias migrate="python manage.py migrate"
alias collectstatic="python manage.py collectstatic"
alias createsuperuser="python manage.py createsuperuser"

# React
alias create="npx create-react-app"
alias gd="gatsby develop"

# System
alias update="sudo pacman -Syyy"
alias install="sudo pacman -Syu"
alias postgres="sudo -u postgres psql"
alias venv="source ~/venv/bin/activate"

# ==================================
# Git Commands
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
# SSH
# ==================================
alias spb="cat ~/.ssh/id_rsa.pub"
alias spv="cat ~/.ssh/id_rsa"

# ==================================
# Custom Functions
# ==================================
function mkcd() {
    mkdir $1 && cd $1
}

# ==================================
# NVM Configuration
# ==================================
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"