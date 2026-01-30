# Installation & Prerequisites

## Neovim Installation

### macOS

```bash
# Using Homebrew
brew install neovim

# Verify installation
nvim --version  # Should be >= 0.11.0
```

### Linux (Ubuntu/Debian)

```bash
# Ubuntu 24.04+ has recent version
sudo apt update
sudo apt install neovim

# For older Ubuntu versions, use snap
sudo snap install nvim --classic

# Or build from source
sudo apt install ninja-build gettext cmake unzip curl build-essential
git clone https://github.com/neovim/neovim
cd neovim
git checkout stable
make CMAKE_BUILD_TYPE=RelWithDebInfo
sudo make install
```

### Arch Linux

```bash
sudo pacman -S neovim
```

### Windows

```powershell
# Using Scoop
scoop install neovim

# Using Chocolatey
choco install neovim
```

## Essential Dependencies

### Node.js (for LSP servers)

```bash
# macOS
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version  # Should be >= 18.x
npm --version
```

### Python (for Python LSP & debugging)

```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv

# Verify
python3 --version  # Should be >= 3.8
pip3 --version
```

### Rust (for some tools)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### Git

```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# Verify
git --version
```

## Recommended Tools

### ripgrep (for fast searching)

```bash
# macOS
brew install ripgrep

# Ubuntu/Debian
sudo apt install ripgrep

# Verify
rg --version
```

### fd (for fast file finding)

```bash
# macOS
brew install fd

# Ubuntu/Debian
sudo apt install fd-find

# Verify
fd --version
```

### lazygit (for Git UI)

```bash
# macOS
brew install lazygit

# Ubuntu/Debian
LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
tar xf lazygit.tar.gz lazygit
sudo install lazygit /usr/local/bin
```

### Clipboard Support

```bash
# macOS - built-in

# Ubuntu/Debian
sudo apt install xclip  # X11
sudo apt install wl-clipboard  # Wayland
```

## Directory Structure

Create the Neovim config directory:

```bash
# Create config directory
mkdir -p ~/.config/nvim

# Create data directory (auto-created but good to know)
# ~/.local/share/nvim/

# Backup existing config (if any)
mv ~/.config/nvim ~/.config/nvim.backup.$(date +%Y%m%d)
```

## Verify Installation

Check if everything is installed correctly:

```bash
nvim --version
node --version
python3 --version
git --version
rg --version
fd --version
```

Create a health check in Neovim:

```bash
nvim
```

Then inside Neovim:

```vim
:checkhealth
```

This will show you what's working and what needs to be installed.

## Next Steps

1. ✅ Install Prerequisites
2. 📦 [Set up Plugin Manager](./02-plugin-manager.md)
3. 🔧 [Configure LSP](./03-lsp-setup.md)

## Troubleshooting

### Neovim version too old

If `apt install neovim` gives you an old version:

```bash
sudo snap install nvim --classic
# Create alias in ~/.bashrc or ~/.zshrc
alias nvim='snap run nvim'
```

### Python provider issues

```bash
# Install pynvim
pip3 install --user pynvim

# In Neovim, check:
:checkhealth provider
```

### Node.js provider issues

```bash
# Install neovim npm package
npm install -g neovim

# In Neovim, check:
:checkhealth provider
```

### Clipboard not working

```bash
# Linux X11
sudo apt install xclip

# Linux Wayland
sudo apt install wl-clipboard

# Then in Neovim:
:checkhealth clipboard
```
