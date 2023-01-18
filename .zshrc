# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Use powerline
USE_POWERLINE="true"
HOST_NAME=kneeraazon

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

#antigen bundle zsh-users/zsh-autosuggestions
source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

#
plugins=(git 
	rake
  web-search
	zsh-autosuggestions)
source $ZSH/oh-my-zsh.sh

autoload -Uz history-beginning-search-menu
zle -N history-beginning-search-menu
bindkey '^X^X' history-beginning-search-menu

alias ll="ls -la"
alias cl="clear"
alias ether="sudo modprobe r8169"
export ZSH="/home/kneeraazon/.oh-my-zsh"

# https://github.com/zsh-users/zsh-syntax-highlighting/blob/master/INSTALL.md
source $ZSH/oh-my-zsh.sh

function mkcd()
{
    mkdir $1 && cd $1
}

# -------
# Aliases
# -------
alias a='code .'
alias c='code .'
alias ns='npm start'
alias start='npm start'
alias nr='npm run'
alias run='npm run'
alias nis='npm i -S'
alias l="ls" # List files in current directory
alias ll="ls -al" # List all files in current directory in long list format
alias sudo='sudo '
alias nrd="npm run develop"
alias gd="gatsby develop"

# ----------------------
# Git Aliases
# ----------------------
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

#Aliases
alias cp="cp -i"                          # confirm before overwriting something
alias df='df -h'                          # human-readable sizes
alias free='free -m'                      # show sizes in MB
alias np='nano -w PKGBUILD'
alias more=less

#Dir Navigation  Aliases

alias l="ls" # List files in current directory
alias ll="ls -al" # List all files in current directory in long list format
alias cd..='cd ..'


# watchers managing react maa
alias watchers="echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p"

#System Aliases
alias update="sudo pacman -Syyy"
alias install="sudo pacman -Syu"
alias postgres="sudo -u postgres psql"
alias bashrc="subl3 ~/.bashrc"
#Virtual Env Activate
alias venv="source ~/venv/bin/activate"

#Djngo Command aliases
alias runserver="python manage.py runserver"
alias makemigrations="python manage.py makemigrations"
alias migrate="python manage.py migrate"
alias collectstatic="python manage.py collectstatic"
alias createsuperuser="python manage.py createsuperuser"
# React
alias create="npx create-react-app"

alias ns='npm start'
alias start='npm start'
alias nr='npm run'
alias run='npm run'
alias nis='npm i -S'

# SSH Key
alias skpb="cat ~/.ssh/id_rsa.pub"
alias skpv="cat ~/.ssh/id_rsa"

source ~/powerlevel10k/powerlevel10k.zsh-theme

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
