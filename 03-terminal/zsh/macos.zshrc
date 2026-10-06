# ==================================
# macOS Zsh Configuration
# ==================================

# ==================================
# PATH & Environment
# ==================================
export PATH="$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH"

# Homebrew (Apple Silicon path; Intel uses /usr/local)
if [ -d "/opt/homebrew/bin" ]; then
  export PATH="/opt/homebrew/bin:$PATH"
  export HOMEBREW_PREFIX="/opt/homebrew"
fi

export ZSH="$HOME/.oh-my-zsh"
export HOST_NAME=kneeraazon

# Python 3 as default (no 'export alias' — that is invalid syntax)
alias python='python3'
alias pip='pip3'

# ==================================
# Oh-My-Zsh Configuration
# ==================================
ZSH_THEME="robbyrussell"

plugins=(
  git
  zsh-autosuggestions
  zsh-syntax-highlighting
  fzf
  history
  macos       # macOS-specific shortcuts (open, ofd, cdf, etc.)
)

source $ZSH/oh-my-zsh.sh
export USE_POWERLINE="true"

# ==================================
# Key Bindings & History
# ==================================
HISTSIZE=10000
SAVEHIST=20000
HISTFILE=~/.zsh_history
setopt APPEND_HISTORY
setopt SHARE_HISTORY
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_VERIFY
setopt INC_APPEND_HISTORY

# Case-insensitive completion
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

# ==================================
# File Operations
# ==================================
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
alias df='df -h'
alias free='vm_stat | awk "/Pages free/ {print \$3 * 4096 / 1048576 \" MB free\"}"'
alias more=less

alias l='ls'
alias ll='ls -alh'
alias la='ls -lahF'

mkcd() { mkdir -p "$1" && cd "$1"; }
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# ==================================
# System — Homebrew
# ==================================
alias update='brew update && brew upgrade'
alias install='brew install'
alias remove='brew uninstall'
alias search-pkg='brew search'
alias show-pkg='brew info'
alias cleanup='brew cleanup'
alias doctor='brew doctor'

# ==================================
# Development — Editors
# ==================================
alias c="open -a 'Visual Studio Code' ."
alias code="open -a 'Visual Studio Code' ."
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
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

alias ns='npm start'
alias nr='npm run'
alias ni='npm install'
alias nis='npm i -S'
alias nid='npm i -D'
alias create='npx create-react-app'

# ==================================
# Development — PostgreSQL
# ==================================
alias postgres='sudo -u postgres psql'

# ==================================
# Network & Security
# ==================================
alias myip='curl -s ifconfig.me'
alias localip='ipconfig getifaddr en0'
alias ports='lsof -i -P -n | grep LISTEN'
alias spb='cat ~/.ssh/id_rsa.pub'
alias spv='cat ~/.ssh/id_rsa'
alias flush-dns='sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder'

# ==================================
# Custom Functions
# ==================================
mkcd() { mkdir -p "$1" && cd "$1"; }

hgrep() { history | grep "$1"; }

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

# Quick look at man page
cheat() { curl "cheat.sh/$1"; }

# Show top 10 largest files/folders in current dir
biggest() { du -sh ./* | sort -rh | head -10; }

# ==================================
# Final Initializations
# ==================================
eval "$(starship init zsh)"

# fzf key bindings and completion
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
