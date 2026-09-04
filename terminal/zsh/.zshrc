export PATH="/home/kneeraazon/.config/nvm/versions/node/v24.18.0/bin:$PATH"
# =============================================================================
#  ~/.zshrc — kneeraazon
#  CachyOS · KDE Plasma 6 · Wayland · Gruvbox Dark Hard
#  Prompt: starship
# =============================================================================

# ─── XDG base directories ────────────────────────────────────────────────────
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"

# ─── Core environment ─────────────────────────────────────────────────────────
export ZSH="$HOME/.oh-my-zsh"
export EDITOR="nvim"
export VISUAL="nvim"
export PAGER="less"
export LESS="-R --use-color -Dd+r -Du+b"
export MANPAGER="nvim +Man!"

# AMD RDNA2 (RX 6700 XT) — ROCm compatibility mode
export HSA_OVERRIDE_GFX_VERSION=10.3.0

# Ollama — local LLM inference
export OLLAMA_HOST="0.0.0.0:11434"
export OLLAMA_DEFAULT_MODEL="llama3.2:3b"

# Build caches
export RUSTC_WRAPPER=sccache
export SCCACHE_CACHE_SIZE=10G

# pnpm
export PNPM_HOME="$HOME/.local/share/pnpm"

# ─── PATH (single source, auto-deduped) ──────────────────────────────────────
typeset -U path PATH
path=(
  "$HOME/.local/bin"
  "$HOME/focus/scripts"
  "$PNPM_HOME"
  "/usr/lib/ccache/bin"
  $path
)
[[ -f "$HOME/.local/bin/env" ]] && source "$HOME/.local/bin/env"
[[ -f "$HOME/.cargo/env"     ]] && source "$HOME/.cargo/env"

# ─── Secrets ──────────────────────────────────────────────────────────────────
[[ -f "$XDG_CONFIG_HOME/zsh/private.zsh" ]] && source "$XDG_CONFIG_HOME/zsh/private.zsh"

# ─── Oh My Zsh ────────────────────────────────────────────────────────────────
# No OMZ theme — starship owns the prompt.
ZSH_THEME=""
DISABLE_AUTO_UPDATE=true
ZSH_AUTOSUGGEST_USE_ASYNC=true

# ── history-substring-search must be configured before OMZ loads ───────────────
HISTORY_SUBSTRING_SEARCH_HIGHLIGHT_FOUND='bg=239,fg=142,bold'
HISTORY_SUBSTRING_SEARCH_HIGHLIGHT_NOT_FOUND='bg=239,fg=167,bold'
HISTORY_SUBSTRING_SEARCH_FUZZY=true

plugins=(
  # ── OMZ built-ins: core ───────────────────────────────────────────────────────
  git sudo fzf history web-search
  colored-man-pages command-not-found
  docker docker-compose kubectl npm
  copyfile copypath copybuffer dirhistory
  history-substring-search

  # ── OMZ built-ins: productivity ──────────────────────────────────────────────
  aliases            # `als` — lists all defined aliases, searchable
  alias-finder       # suggests shortest alias as you type full commands
  encode64           # encode64 / decode64 / e64 / d64 for base64
  jsontools          # pp_json, is_json — pretty-print and validate JSON
  urltools           # urlencode / urldecode
  safe-paste         # prevents accidental execution of multi-line paste
  systemd            # sc-start, sc-stop, sc-status, sc-restart, etc.
  pip                # pip completion + pip-requirements helper

  # ── third-party: zsh-defer FIRST so deferred loads work ──────────────────────
  zsh-defer
  fzf-tab

  # ── MUST be last ─────────────────────────────────────────────────────────────
  zsh-syntax-highlighting
)
# zsh-autosuggestions and you-should-use are deferred below (after OMZ source)

source "$ZSH/oh-my-zsh.sh"
[[ -f "$HOME/.fzf.zsh" ]] && source "$HOME/.fzf.zsh"

# ── history-substring-search keybindings (after OMZ, avoids override) ─────────
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down
bindkey -M emacs '^P' history-substring-search-up
bindkey -M emacs '^N' history-substring-search-down

# ── Item 1: deferred plugin loading — prompt appears instantly ─────────────────
zsh-defer source "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh"
zsh-defer source "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/you-should-use/you-should-use.plugin.zsh"

# ── Item 2: atuin — SQLite history with rich Ctrl+R TUI ───────────────────────
# ↑↓ kept for history-substring-search; atuin owns Ctrl+R
command -v atuin >/dev/null 2>&1 && zsh-defer eval "$(atuin init zsh --disable-up-arrow)"

# ─── fzf-tab configuration ────────────────────────────────────────────────────
if [[ -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/fzf-tab" ]]; then
  zstyle ':fzf-tab:complete:cd:*'          fzf-preview 'eza --tree --color=always --icons --level=2 $realpath'
  zstyle ':fzf-tab:complete:*:*'           fzf-preview '~/.config/fzf/preview.sh $realpath'
  zstyle ':fzf-tab:*' switch-group '<' '>'
  zstyle ':completion:*' menu no
fi

# ─── FZF configuration ────────────────────────────────────────────────────────
export FZF_DEFAULT_OPTS="
  --color=bg+:#3c3836,bg:#1d2021,spinner:#fb4934,hl:#928374
  --color=fg:#ebdbb2,header:#928374,info:#8ec07c,pointer:#fb4934
  --color=marker:#fb4934,fg+:#ebdbb2,prompt:#fb4934,hl+:#fb4934
  --color=border:#504945,label:#ebdbb2,query:#ebdbb2
  --border=rounded --padding=0,1
  --height=40% --layout=reverse --info=inline-right
  --separator='─'
  --bind 'ctrl-/:toggle-preview'
  --bind 'ctrl-space:toggle'
  --bind 'alt-a:select-all'
"

if command -v fd >/dev/null 2>&1; then
  export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git --exclude node_modules --exclude __pycache__ --exclude .venv'
  export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
fi

export FZF_CTRL_T_OPTS="
  --preview '~/.config/fzf/preview.sh {}'
  --preview-window='right:60%:border-left:wrap'
  --bind 'ctrl-/:toggle-preview'
  --bind 'alt-p:toggle-preview'
"
export FZF_ALT_C_OPTS="
  --preview 'eza --tree --color=always --icons --level=2 {}'
  --preview-window='right:50%:border-left'
"
export FZF_CTRL_R_OPTS="
  --preview 'echo {}'
  --preview-window=down:3:hidden:wrap
  --bind 'ctrl-/:toggle-preview'
  --layout=reverse --height=40%
"

# ─── Shell options ────────────────────────────────────────────────────────────
HISTFILE="$HOME/.zsh_history"
HISTSIZE=100000
SAVEHIST=100000
setopt APPEND_HISTORY SHARE_HISTORY INC_APPEND_HISTORY
setopt HIST_IGNORE_ALL_DUPS HIST_FIND_NO_DUPS HIST_IGNORE_SPACE
setopt HIST_REDUCE_BLANKS HIST_VERIFY

setopt AUTO_CD AUTO_PUSHD PUSHD_IGNORE_DUPS PUSHD_SILENT
setopt EXTENDED_GLOB NO_CASE_GLOB INTERACTIVE_COMMENTS

# ─── Gruvbox Dark Hard palette ───────────────────────────────────────────────
typeset -gA GRUVBOX
GRUVBOX=(
  bg0  "29;32;33"     bg1  "60;56;54"     bg2  "80;73;69"
  fg   "235;219;178"  fg4  "168;153;132"  gray "146;131;116"
  red    "204;36;29"   green  "152;151;26"  yellow "215;153;33"
  blue   "69;133;136"  purple "177;98;134"  aqua   "104;157;106"
  orange "214;93;14"
  br_red    "251;73;52"   br_green  "184;187;38"  br_yellow "250;189;47"
  br_blue   "131;165;152" br_purple "211;134;155" br_aqua   "142;192;124"
  br_orange "254;128;25"
)

# ─── LS_COLORS / EZA_COLORS ──────────────────────────────────────────────────
export LS_COLORS="\
di=01;38;2;117;50;84:\
ln=38;2;104;157;106:\
so=38;2;177;98;134:\
pi=38;2;214;93;14:\
ex=38;2;152;151;26:\
bd=38;2;69;133;136;48;2;60;56;54:\
cd=38;2;69;133;136;48;2;60;56;54:\
su=38;2;251;73;52:\
sg=38;2;251;73;52:\
tw=38;2;152;151;26:\
ow=38;2;152;151;26:\
or=38;2;251;73;52;48;2;40;40;40:\
mi=38;2;251;73;52"

export EZA_COLORS="\
di=01;38;2;117;50;84:\
ln=38;2;104;157;106:\
ex=38;2;152;151;26:\
da=38;2;146;131;116:\
uu=38;2;184;187;38:\
gu=38;2;131;165;152:\
sn=38;2;104;157;106:\
sb=38;2;104;157;106:\
ur=38;2;69;133;136:\
uw=38;2;214;93;14:\
ux=38;2;152;151;26:\
ue=38;2;152;151;26:\
gr=38;2;69;133;136:\
gw=38;2;214;93;14:\
gx=38;2;152;151;26:\
tr=38;2;69;133;136:\
tw=38;2;214;93;14:\
tx=38;2;152;151;26:\
xx=38;2;146;131;116"

command -v bat >/dev/null 2>&1 && export BAT_THEME="gruvbox-dark"

# ─── Completion ───────────────────────────────────────────────────────────────
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' group-name ''
zstyle ':completion:*:descriptions' format '%F{214}── %d ──%f'
zstyle ':completion:*:messages'     format '%F{142}%d%f'
zstyle ':completion:*:warnings'     format '%F{167}no matches%f'
zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*( *[a-z])*=34=31'

if [[ -o interactive ]]; then
  command -v uv  >/dev/null 2>&1 && eval "$(uv generate-shell-completion zsh)"
  command -v uvx >/dev/null 2>&1 && eval "$(uvx --generate-shell-completion zsh)"
fi

# ─── Plugin styling ───────────────────────────────────────────────────────────
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=245'
ZSH_AUTOSUGGEST_STRATEGY=(history completion)

typeset -gA ZSH_HIGHLIGHT_STYLES
ZSH_HIGHLIGHT_STYLES=(
  comment              'fg=245,italic'
  alias                'fg=108'
  suffix-alias         'fg=108'
  global-alias         'fg=108'
  function             'fg=142'
  command              'fg=142'
  builtin              'fg=142'
  precommand           'fg=142,italic'
  autodirectory        'fg=214'
  single-hyphen-option 'fg=214'
  double-hyphen-option 'fg=214'
  back-quoted-argument 'fg=175'
  reserved-word        'fg=167'
  path                 'fg=223'
  path_pathseparator   'fg=245'
)

# ─── you-should-use ───────────────────────────────────────────────────────────
export YSU_MESSAGE_POSITION="after"
export YSU_MODE=ALL
export YSU_MESSAGE_FORMAT="$(printf '\033[38;2;214;93;14m')hint\033[0m  %alias_type: $(printf '\033[38;2;184;187;38m')%alias\033[0m → %command"
export YSU_IGNORED_ALIASES=("g" "v" "c" "n")

# ─── Terminal title ───────────────────────────────────────────────────────────
autoload -Uz add-zsh-hook
_title_precmd()  { printf '\033]0;%s\007' "${(%):-%~}"; }
_title_preexec() { printf '\033]0;%s\007' "$1"; }
add-zsh-hook precmd  _title_precmd
add-zsh-hook preexec _title_preexec

# ─── Formatting helpers ───────────────────────────────────────────────────────
typeset -gA FX
FX=(reset "\033[0m" bold "\033[1m" dim "\033[2m" italic "\033[3m" underline "\033[4m")

typeset -gA CLR
CLR=(
  red     "\033[38;2;204;36;29m"   green   "\033[38;2;152;151;26m"
  yellow  "\033[38;2;215;153;33m"  blue    "\033[38;2;69;133;136m"
  purple  "\033[38;2;177;98;134m"  aqua    "\033[38;2;104;157;106m"
  orange  "\033[38;2;214;93;14m"   gray    "\033[38;2;146;131;116m"
  fg      "\033[38;2;235;219;178m"
)
R="${FX[reset]}"

_sep()  { printf "${CLR[gray]}${FX[dim]}%s${R}\n" "$(printf '%.0s─' {1..60})"; }
_ok()   { printf "  ${CLR[green]}✔${R}  %s\n" "$1"; }
_info() { printf "  ${CLR[aqua]}◆${R}  %s\n" "$1"; }
_warn() { printf "  ${CLR[yellow]}▲${R}  %s\n" "$1"; }
_err()  { printf "  ${CLR[red]}✖${R}  %s\n" "$1"; }
_step() { printf "\n  ${CLR[purple]}▸${R} %s\n" "$1"; }

# ─── Keybindings ─────────────────────────────────────────────────────────────
autoload -Uz history-beginning-search-menu
zle -N history-beginning-search-menu
bindkey '^X^X'    history-beginning-search-menu
bindkey '^[[1;5D' backward-word       # Ctrl+Left
bindkey '^[[1;5C' forward-word        # Ctrl+Right
bindkey '^H'      backward-kill-word  # Ctrl+Backspace
bindkey '^[[3;5~' kill-word           # Ctrl+Delete
bindkey '^[.'     insert-last-word    # Alt+.

# Ctrl+G → lazygit overlay
if command -v lazygit >/dev/null 2>&1; then
  _launch_lazygit() { lazygit; zle reset-prompt; }
  zle -N _launch_lazygit
  bindkey '^G' _launch_lazygit
fi

# ─── Navigation ───────────────────────────────────────────────────────────────
alias cp='cp -iv'
alias mv='mv -iv'
alias rm='rm -Iv'
alias mkdir='mkdir -pv'
alias cl='clear'
alias h='history'
alias reload='exec zsh'
alias zshrc='${EDITOR:-nvim} ~/.zshrc'

alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'

mkcd() { mkdir -p "$1" && cd "$1"; }

# ─── File listing ─────────────────────────────────────────────────────────────
if command -v eza >/dev/null 2>&1; then
  alias ls='eza --icons --group-directories-first'
  alias l='eza -lbF --icons --git --group-directories-first'
  alias ll='eza -lbhiga --time-style=long-iso --color-scale --icons --group-directories-first'
  alias la='eza -labhiga --time-style=long-iso --color-scale --icons --group-directories-first'
  alias lt='eza --tree --level=2 --icons --group-directories-first'
  alias tree='eza --tree --icons'
else
  alias ll='ls -lah'
  alias la='ls -A'
fi

if command -v bat >/dev/null 2>&1; then
  alias cat='bat --style=plain'
  alias catn='bat'
fi

if [[ -o interactive ]] && command -v eza >/dev/null 2>&1; then
  chpwd() {
    emulate -L zsh
    eza -lbF --icons --group-directories-first
  }
fi

# ─── Package management ───────────────────────────────────────────────────────
alias install='paru -S --noconfirm'
alias remove='sudo pacman -Rns --noconfirm'
alias search-pkg='paru -Ss'
alias show-pkg='pacman -Qi'
alias list-installed='pacman -Qe'
alias clean='paru -Sc --noconfirm'
alias aur='paru -S'
alias aurs='paru -Ss'

autoremove() {
  local orphans
  orphans="$(pacman -Qdtq 2>/dev/null)"
  if [[ -z "$orphans" ]]; then
    _info "No orphaned packages"; return 0
  fi
  sudo pacman -Rns --noconfirm ${=orphans}
}

# ─── System monitoring ────────────────────────────────────────────────────────
alias df='df -h'
alias free='free -mh'
alias pstat='systemctl status'
alias psu='ps aux --sort=-%cpu | head -10'
alias psm='ps aux --sort=-%mem | head -10'
command -v btop       >/dev/null 2>&1 && alias top='btop'
command -v amdgpu_top >/dev/null 2>&1 && alias gpumon='amdgpu_top'

# ─── Git ──────────────────────────────────────────────────────────────────────
alias g='git'
alias ga='git add'
alias gaa='git add .'
alias gcm='git commit -m'
alias gacm='git add . && git commit -m'
alias gd='git diff'
alias gds='git diff --staged'
alias gi='git init'
alias gl='git log --oneline --graph --decorate --all'
alias glog='git log --graph --pretty=format:"%C(auto)%h%d %s %C(dim white)- %an, %ar%C(reset)" --all'
alias gcl='git clone'
alias gpl='git pull'
alias gps='git push'
alias gpsh='git pull && git push'
alias gss='git status -s'
alias gst='git status'
alias gcb='git checkout -b'
alias gco='git checkout'
alias gsw='git switch'
alias grs='git restore --staged'
alias gsl='git stash list'
alias gsp='git stash pop'

# ─── Python / Django / FastAPI ────────────────────────────────────────────────
alias py='python3'
alias pip='pip3'

if command -v uv >/dev/null 2>&1; then
  alias uvs='uv sync'
  alias uvr='uv run'
  alias uva='uv add'
  alias uvrm='uv remove'
  alias uvp='uv pip'
fi

alias venv='source ./venv/bin/activate'
alias vmk='python3 -m venv venv && source ./venv/bin/activate'
alias pipr='pip install -r requirements.txt'
alias pipf='pip freeze > requirements.txt'

alias dj='python manage.py'
alias djrun='python manage.py runserver'
alias djmm='python manage.py makemigrations'
alias djm='python manage.py migrate'
alias djsp='python manage.py shell_plus --ipython'
alias djsu='python manage.py createsuperuser'
alias djstatic='python manage.py collectstatic --noinput'
alias djtest='python manage.py test'

alias farun='uvicorn main:app --reload'
alias flrun='flask run'

# ─── Node / npm / Next ────────────────────────────────────────────────────────
alias ni='npm install'
alias ns='npm start'
alias nd='npm run dev'
alias nb='npm run build'
alias nt='npm test'
alias nng='npm install -g'

alias nextdev='npx next dev'
alias nextbuild='npx next build'
alias nextstart='npx next start'

# ─── Docker / Kubernetes ──────────────────────────────────────────────────────
alias d='docker'
alias dco='docker compose'
alias dcup='docker compose up -d'
alias dcdown='docker compose down'
alias dclogs='docker compose logs -f'
alias dcps='docker compose ps'
alias dps='docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
alias dpsa='docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
alias di='docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"'
alias dprune='docker system prune -a --volumes'

dstop() {
  local ids
  ids="$(docker ps -aq 2>/dev/null)"
  [[ -n "$ids" ]] && docker stop ${=ids} || _info "No containers to stop"
}

drm-all() {
  local ids
  ids="$(docker ps -aq 2>/dev/null)"
  [[ -n "$ids" ]] && docker rm ${=ids} || _info "No containers to remove"
}

alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get services'
alias kgd='kubectl get deployments'
alias kl='kubectl logs'
alias kapply='kubectl apply -f'

# ─── Databases ────────────────────────────────────────────────────────────────
alias dredis='docker run --name redis-dev -p 6379:6379 -d redis'
alias dpostgres='docker run --name pg-dev -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres'
alias dmongo='docker run --name mongo-dev -p 27017:27017 -d mongo'
alias pgconnect='docker exec -it pg-dev psql -U postgres'

# ─── Editors / network ────────────────────────────────────────────────────────
alias c='code .'
alias n='nano'
alias vim='nvim'
alias v='nvim'

alias myip='curl -s ifconfig.me && echo'
alias localip="ip -4 addr show | awk '/inet / {print \$2}' | cut -d/ -f1"
alias ports='ss -tulnp'
alias sshconfig='${EDITOR:-nvim} ~/.ssh/config'

# ─── LLM / Ollama ─────────────────────────────────────────────────────────────
if command -v ollama >/dev/null 2>&1; then
  alias oll='ollama'
  alias ollls='ollama list'
  alias ollps='ollama ps'

  llm() {
    [[ -z "$*" ]] && { echo "Usage: llm <prompt>" >&2; return 1; }
    echo "$*" | ollama run "${OLLAMA_DEFAULT_MODEL:-llama3.2:3b}"
  }

  chat() {
    ollama run "${1:-${OLLAMA_DEFAULT_MODEL:-llama3.2:3b}}"
  }
fi

# ─── Cloud ────────────────────────────────────────────────────────────────────
if command -v gcloud >/dev/null 2>&1; then
  for _gc in \
    "$HOME/.config/gcloud/completion.zsh.inc" \
    "/opt/google-cloud-sdk/completion.zsh.inc" \
    "/usr/lib/google-cloud-sdk/completion.zsh.inc"; do
    [[ -f "$_gc" ]] && { source "$_gc"; break; }
  done
  unset _gc
fi

# ─── System utilities ─────────────────────────────────────────────────────────
sysinfo() {
  echo
  _sep
  _info "Hostname:  $(hostname)"
  _info "Kernel:    $(uname -r)"
  _info "Uptime:    $(uptime -p | sed 's/^up //')"
  _info "Packages:  $(pacman -Q | wc -l) installed"
  _info "Shell:     $(basename "$SHELL") $ZSH_VERSION"
  _info "Memory:    $(free -h | awk '/Mem:/ {printf "%s / %s", $3, $2}')"
  _info "Disk /:    $(df -h / | awk 'NR==2 {printf "%s / %s (%s)", $3, $2, $5}')"
  _sep
  echo
}

pacman-history() {
  [[ ! -f /var/log/pacman.log ]] && { _err "Pacman log not found"; return 1; }
  case "$1" in
    install) grep "\[ALPM\] installed" /var/log/pacman.log | tail -20 ;;
    upgrade) grep "\[ALPM\] upgraded"  /var/log/pacman.log | tail -20 ;;
    remove)  grep "\[ALPM\] removed"   /var/log/pacman.log | tail -20 ;;
    *)       _info "Usage: pacman-history {install|upgrade|remove}" ;;
  esac
}

hgrep() { history | grep --color=auto "$1"; }

extract() {
  [[ ! -f "$1" ]] && { _err "'$1' is not a valid file"; return 1; }
  _info "Extracting ${CLR[fg]}$1${R}"
  case "$1" in
    *.tar.bz2) tar xjf "$1" ;;
    *.tar.gz)  tar xzf "$1" ;;
    *.tar.xz)  tar xJf "$1" ;;
    *.tar.zst) tar --zstd -xf "$1" ;;
    *.bz2)     bunzip2 "$1" ;;
    *.rar)     unrar x "$1" ;;
    *.gz)      gunzip "$1" ;;
    *.tar)     tar xf "$1" ;;
    *.tbz2)    tar xjf "$1" ;;
    *.tgz)     tar xzf "$1" ;;
    *.zip)     unzip "$1" ;;
    *.7z)      7z x "$1" ;;
    *.zst)     unzstd "$1" ;;
    *)         _err "Unknown archive format: '$1'"; return 1 ;;
  esac
  _ok "Done"
}

scaffold() {
  local name="${1:-myproject}"
  mkcd "$name" || return
  git init -q
  touch README.md .gitignore
  _ok "Project '$name' created"
}

# ─── Full system update ───────────────────────────────────────────────────────
update() {
  local start=$SECONDS rc=0 flatpak_rc=0 elapsed mins secs orphans

  echo
  printf "  ${CLR[aqua]}╭─────────────────────────────────╮${R}\n"
  printf "  ${CLR[aqua]}│   🚀  System Update Starting    │${R}\n"
  printf "  ${CLR[aqua]}╰─────────────────────────────────╯${R}\n"

  if ! command -v paru >/dev/null 2>&1; then
    _err "paru not found"; return 1
  fi

  _step "Syncing repositories and upgrading packages"
  _sep
  paru -Syu --devel --noconfirm --combinedupgrade --sudoloop
  rc=$?
  (( rc == 0 )) && _ok "Packages up to date" || _warn "paru exited $rc"

  if command -v flatpak >/dev/null 2>&1; then
    _step "Updating Flatpak packages"
    _sep
    flatpak update --noninteractive
    flatpak_rc=$?
    (( flatpak_rc == 0 )) && _ok "Flatpak up to date" || _warn "flatpak exited $flatpak_rc"
  fi

  orphans="$(pacman -Qdtq 2>/dev/null)"
  if [[ -n "$orphans" ]]; then
    _step "Removing orphaned packages"
    _sep
    sudo pacman -Rns --noconfirm ${=orphans}
    _ok "Orphans removed"
  else
    _info "No orphaned packages"
  fi

  _step "Cleaning package cache"
  _sep
  paru -Sc --noconfirm 2>/dev/null
  _ok "Cache cleaned"

  elapsed=$((SECONDS - start))
  mins=$((elapsed / 60)); secs=$((elapsed % 60))

  echo
  printf "  ${CLR[green]}╭─────────────────────────────────╮${R}\n"
  printf "  ${CLR[green]}│   ✅  Update complete           │${R}\n"
  printf "  ${CLR[green]}│   ⏱  %2dm %02ds elapsed          │${R}\n" "$mins" "$secs"
  printf "  ${CLR[green]}╰─────────────────────────────────╯${R}\n"
  echo
}

alias upgrade='update'
alias fullupdate='update'

# ─── Modern CLI replacements ──────────────────────────────────────────────────
command -v dust       >/dev/null 2>&1 && alias du='dust'
command -v procs      >/dev/null 2>&1 && alias ps='procs'
command -v lazygit    >/dev/null 2>&1 && alias lg='lazygit'
command -v lazydocker >/dev/null 2>&1 && alias ld='lazydocker'
command -v btop       >/dev/null 2>&1 && alias top='btop'
command -v pgcli      >/dev/null 2>&1 && alias pg='pgcli'
command -v http       >/dev/null 2>&1 && alias rest='http'
command -v yazi       >/dev/null 2>&1 && alias fm='yazi'
command -v just       >/dev/null 2>&1 && alias j='just'
command -v dive       >/dev/null 2>&1 && alias dv='dive'

# pgexplain <connstring-or-dbname> <query> — EXPLAIN (ANALYZE, BUFFERS) via
# pgcli's own formatting, without opening an interactive session.
pgexplain() {
  if [ $# -lt 2 ]; then
    echo "usage: pgexplain <dbname-or-connstring> \"<query>\"" >&2
    return 1
  fi
  local target="$1"; shift
  pgcli "$target" -e "EXPLAIN (ANALYZE, BUFFERS) $*"
}

# ─── Tool integrations ────────────────────────────────────────────────────────

# zoxide — smarter cd, ranks by frecency (z <partial>, zi for interactive)
if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh)"
  alias cd='z'
fi

# direnv — per-project env vars from .envrc
command -v direnv >/dev/null 2>&1 && eval "$(direnv hook zsh)"

# mise — polyglot runtime version manager (node/python/etc via .mise.toml)
command -v mise >/dev/null 2>&1 && eval "$(mise activate zsh)"

# tealdeer — tldr pages, community-maintained cheatsheets
command -v tldr >/dev/null 2>&1 && alias help='tldr'


# Item 4: carapace — universal completion engine (500+ commands)
if command -v carapace >/dev/null 2>&1; then
  export CARAPACE_BRIDGES='zsh,fish,bash'
  zstyle ':completion:*' format $'\e[2;38;2;146;131;116mCompleting %d\e[m'
  source <(carapace _carapace zsh)
fi

# Item 6: navi — interactive cheatsheet TUI (Alt+G to avoid Ctrl+G=lazygit)
if command -v navi >/dev/null 2>&1; then
  eval "$(navi widget zsh)"
  bindkey '^[g' _navi_widget   # Alt+G
fi

# ─── psql in dedicated kitty window ──────────────────────────────────────────
psql() {
  kitty --config "$HOME/.config/kitty/psql-mode.conf" -- /usr/bin/psql "$@"
}

# ─── Power functions ──────────────────────────────────────────────────────────

# fzf-powered process killer
fkill() {
  local pid
  pid=$(ps aux | sed 1d | fzf -m --header="Select process(es) to kill" \
    --preview 'echo {}' --preview-window=down:2:wrap | awk '{print $2}')
  [[ -n "$pid" ]] && echo "$pid" | xargs kill -"${1:-9}" && echo "Killed: $pid"
}

# fzf git branch switcher with log preview  (use: gfbr)
gfbr() {
  local branch
  branch=$(git branch -a --color=always 2>/dev/null | grep -v '/HEAD\s' | sort |
    fzf --ansi --preview "git log --oneline --graph --color=always \
      --format='%C(auto)%h%d %s %C(dim white)%an, %ar' \
      \$(sed s/^..// <<< {} | cut -d' ' -f1) -- 2>/dev/null | head -40" |
    sed 's/^..//' | cut -d' ' -f1 | sed 's|^remotes/[^/]*/||')
  [[ -n "$branch" ]] && git switch "$branch"
}

# fzf git log browser — Enter to show full diff
gfl() {
  git log --oneline --color=always 2>/dev/null |
    fzf --ansi \
      --preview 'git show --stat --color=always {1}' \
      --bind 'enter:execute(git show --color=always {1} | less -R)'
}

# fzf docker container shell (falls back to sh if bash absent)
dsh() {
  local cid
  cid=$(docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}' 2>/dev/null |
    fzf --header="Select container" | awk '{print $1}')
  [[ -z "$cid" ]] && return 1
  docker exec -it "$cid" "${1:-bash}" 2>/dev/null || docker exec -it "$cid" sh
}

# fuzzy find and edit file
fe() {
  local file
  file=$(fd --type f --hidden --follow --exclude .git --exclude node_modules 2>/dev/null |
    fzf --preview '~/.config/fzf/preview.sh {}')
  [[ -n "$file" ]] && ${EDITOR:-nvim} "$file"
}

# fuzzy cd into any directory
fcd() {
  local dir
  dir=$(fd --type d --hidden --follow --exclude .git --exclude node_modules 2>/dev/null |
    fzf --preview 'eza --tree --color=always --icons --level=2 {}')
  [[ -n "$dir" ]] && cd "$dir"
}

# quick HTTP server in current dir
serve() {
  local port="${1:-8000}"
  _info "Serving ${CLR[fg]}$(pwd)${R} at ${CLR[br_green]}http://localhost:$port${R}"
  python3 -m http.server "$port"
}

# show what's occupying a port
port() {
  [[ -z "$1" ]] && { _warn "Usage: port <number>"; return 1; }
  ss -tulnp | grep ":$1 "
}

# create a temp dir and cd into it
tmp() {
  local d; d=$(mktemp -d)
  _info "Created ${CLR[fg]}$d${R}"
  cd "$d"
}

# show PATH one entry per line
path-show() { echo "$PATH" | tr ':' '\n' | nl; }

# show disk usage of current dir sorted by size
duh() { du -h --max-depth="${1:-1}" . | sort -h; }

# colorized env with fzf filter
envf() { env | sort | fzf --preview 'echo {}'; }

# ─── Additional aliases ───────────────────────────────────────────────────────
alias ip='ip -c'               # colorized ip output
alias diff='diff --color=auto'
alias grep='grep --color=auto'
alias pgrep='pgrep -a'
alias watch='watch -c'
alias du='du -h'
alias ping='ping -c 5'
alias wget='wget -c'           # resume by default
alias rsync='rsync -avz --progress'
alias clip='xclip -selection clipboard'
alias open='xdg-open'
# wallpaper           interactive WallRizz picker over ~/.wallpapers
# wallpaper <name>     preview (kitty graphics protocol, if available) and
#                      apply a specific wallpaper by filename or path
wallpaper() {
  local dir="$HOME/.wallpapers"
  if [ $# -eq 0 ]; then
    wallrizz -d "$dir"
    return
  fi
  local target="$1"
  [ -f "$target" ] || target="$dir/$1"
  if [ ! -f "$target" ]; then
    echo "wallpaper: not found: $1 (looked in $dir)" >&2
    return 1
  fi
  if [ -n "$KITTY_WINDOW_ID" ] && command -v kitten >/dev/null 2>&1; then
    kitten icat "$target"
  fi
  ~/.config/hypr/scripts/wallpaper.sh "$target"
}

# quick git aliases not already defined by OMZ git plugin
alias gundo='git reset HEAD~1 --mixed'
alias gdiff='git diff --stat'
alias gcfix='git commit --fixup'
alias gtag='git tag'
alias gstash='git stash'

# ─── Prompt initialisation ────────────────────────────────────────────────────
eval "$(starship init zsh)"

export NVM_DIR="$HOME/.config/nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# kimi-code
export PATH="/home/kneeraazon/.kimi-code/bin:$PATH"
