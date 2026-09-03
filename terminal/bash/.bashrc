
# ~/.bashrc — Arch Linux Bash Configuration
# ============================================================
# NOTE: Git global settings belong in ~/.gitconfig, not here.
#       Run `git config --global ...` once in your terminal
#       to set them permanently.
# ============================================================

HOST_NAME=kneeraazon

# ==================================
# PATH & Environment
# ==================================
export PATH="$HOME/bin:$HOME/.local/bin:$PATH"
export PATH="$HOME/.yarn/bin:$HOME/.config/yarn/global/node_modules/.bin:$PATH"

export DENO_INSTALL="$HOME/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"

export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoredups:erasedups   # No duplicate history entries

export CLICOLOR=1
export LSCOLORS='Gxfxcxdxbxegedabagacad'
export LS_COLORS='di=04;35:ln=01;36:ex=01;32:*.tar=01;31:*.gz=01;31:*.zip=01;31:*.jpg=01;35:*.png=01;35:*.mp3=01;35:*.wav=01;35:'

# ==================================
# Terminal & Prompt
# ==================================
# Coloured Git branch in prompt
git_branch() {
  git branch 2>/dev/null | grep '^\*' | sed 's/^\* //'
}

txtred='\e[0;31m'
txtgrn='\e[0;32m'
bldgrn='\e[1;32m'
bldpur='\e[1;35m'
txtrst='\e[0m'

PS1="\[\033[38m\]\u\[\033[32m\] \w \[\033[31m\]\$(git_branch)\[\033[37m\]\$ \[\033[00m\]"

# History search with arrow keys
bind '"\e[A": history-search-backward'
bind '"\e[B": history-search-forward'

# ==================================
# NVM — Node Version Manager
# ==================================
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# ==================================
# File Operations
# ==================================
alias cp='cp -i'          # Confirm before overwriting
alias mv='mv -i'          # Confirm before moving
alias rm='rm -i'          # Confirm before removing
alias df='df -h'          # Human-readable disk space
alias free='free -m'      # Show memory in MB
alias more=less

# ls aliases
if ls --color > /dev/null 2>&1; then
  colorflag="--color"
else
  colorflag="-G"
fi
alias ls="command ls ${colorflag}"
alias l='ls'
alias ll='ls -alh'
alias la='ls -lahF'

# Directory navigation
mkcd() { mkdir -p "$1" && cd "$1"; }
alias cd..='cd ..'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# ==================================
# System — Package Management (Arch)
# ==================================
alias update='sudo pacman -Syu'
alias install='sudo pacman -S'
alias remove='sudo pacman -R'
alias purge='sudo pacman -Rns'
alias autoremove='sudo pacman -Rns $(pacman -Qdtq 2>/dev/null)'
alias clean='sudo pacman -Sc'
alias search-pkg='pacman -Ss'
alias show-pkg='pacman -Qi'

# Yay (AUR helper) — only if installed
if command -v yay &>/dev/null; then
  alias aur-update='yay -Syu'
  alias aur-install='yay -S'
  alias aur-search='yay -Ss'
fi

# System monitoring
alias top='htop'
alias psu='ps aux --sort=-%cpu | head -10'
alias psm='ps aux --sort=-%mem | head -10'
alias pstat='systemctl status'

# React file-watcher limit
alias watchers='echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p'

# ==================================
# Development — Editors
# ==================================
alias c='code .'
alias nv='nvim'
alias v='vim'

# ==================================
# Development — Git
# ==================================
alias ga='git add'
alias gaa='git add .'
alias gaaa='git add -A'
alias gc='git commit'
alias gcm='git commit -m'
alias gcl='git clone'
alias gd='git diff'
alias gi='git init'
alias gl='git log --oneline --graph --decorate'
alias gpl='git pull'
alias gps='git push'
alias gpsh='git pull && git push'
alias gss='git status -s'
alias gacm='git add . && git commit -m'
alias gs='git status'
alias grb='git rebase'
alias gst='git stash'
alias gstp='git stash pop'

# ==================================
# Development — Python / Django
# ==================================
alias venv='source ./venv/bin/activate'
alias runserver='python manage.py runserver'
alias makemigrations='python manage.py makemigrations'
alias migrate='python manage.py migrate'
alias createsuperuser='python manage.py createsuperuser'
alias collectstatic='python manage.py collectstatic'

# ==================================
# Development — JavaScript / Node.js
# ==================================
alias ns='npm start'
alias nr='npm run'
alias ni='npm install'
alias nis='npm i -S'
alias nid='npm i -D'
alias create='npx create-react-app'
alias gd='gatsby develop'

# ==================================
# Network & Security
# ==================================
alias myip='curl -s ifconfig.me'
alias ports='netstat -tulanp'
alias skpb='cat ~/.ssh/id_rsa.pub'
alias skpv='cat ~/.ssh/id_rsa'

# ==================================
# Custom Functions
# ==================================
# Extract any archive type
extract() {
  if [ -f "$1" ]; then
    case "$1" in
      *.tar.bz2) tar xjf "$1" ;;
      *.tar.gz)  tar xzf "$1" ;;
      *.bz2)     bunzip2 "$1" ;;
      *.rar)     unrar x "$1" ;;
      *.gz)      gunzip "$1" ;;
      *.tar)     tar xf "$1" ;;
      *.tbz2)    tar xjf "$1" ;;
      *.tgz)     tar xzf "$1" ;;
      *.zip)     unzip "$1" ;;
      *.7z)      7z x "$1" ;;
      *)         echo "'$1' cannot be extracted via extract()" ;;
    esac
  else
    echo "'$1' is not a valid file"
  fi
}

# Search command history
hgrep() { history | grep "$1"; }

# Show pacman install/upgrade/remove log
pacman-history() {
  if [ -f /var/log/pacman.log ]; then
    case "$1" in
      install)  grep "installed" /var/log/pacman.log ;;
      upgrade)  grep "upgraded" /var/log/pacman.log ;;
      remove)   grep "removed"  /var/log/pacman.log ;;
      *)        echo "Usage: pacman-history (install|upgrade|remove)" ;;
    esac
  else
    echo "Pacman log not found at /var/log/pacman.log"
  fi
}

# Fabricator task completion
_fab_completion() {
  COMPREPLY=()
  /usr/bin/which -s fab || return 0
  [[ -e fabfile.py ]] || return 0
  local cur="${COMP_WORDS[COMP_CWORD]}"
  tasks=$(fab --shortlist)
  COMPREPLY=( $(compgen -W "${tasks}" -- ${cur}) )
}
complete -F _fab_completion fab
