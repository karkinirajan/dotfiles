# Plugin Manager Setup (lazy.nvim)

## Why lazy.nvim?

- **Modern**: Built specifically for Neovim 0.8+
- **Fast**: Lazy-loads plugins efficiently
- **Simple**: Clean, minimal configuration
- **Features**: Auto-installation, lockfile support, UI for updates

## Installation

Add this to `~/.config/nvim/init.lua`:

```lua
-- Bootstrap lazy.nvim
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable",
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-- Configure leader key (must be before lazy setup)
vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

-- Setup lazy.nvim
require("lazy").setup({
  -- Plugins will go here
}, {
  ui = {
    border = "rounded",
  },
  performance = {
    rtp = {
      disabled_plugins = {
        "gzip",
        "tarPlugin",
        "tohtml",
        "tutor",
        "zipPlugin",
      },
    },
  },
})
```

## Plugin Structure

### Option 1: Single File (Simple)

`~/.config/nvim/init.lua`:

```lua
require("lazy").setup({
  -- Plugin specs here
  { "nvim-lua/plenary.nvim" },
  { "nvim-tree/nvim-web-devicons" },
  -- More plugins...
})
```

### Option 2: Modular (Recommended)

```bash
~/.config/nvim/
├── init.lua              -- Entry point
└── lua/
    ├── config/
    │   ├── options.lua   -- Neovim options
    │   ├── keymaps.lua   -- Key mappings
    │   └── autocmds.lua  -- Autocommands
    └── plugins/
        ├── init.lua      -- Plugin loader
        ├── ui.lua        -- UI plugins
        ├── lsp.lua       -- LSP plugins
        ├── completion.lua
        ├── dap.lua       -- Debugging
        └── ...
```

`init.lua`:

```lua
-- Bootstrap lazy.nvim (as above)
require("lazy").setup("plugins")
require("config.options")
require("config.keymaps")
require("config.autocmds")
```

`lua/plugins/init.lua`:

```lua
return {
  -- Load other plugin files
  { import = "plugins.ui" },
  { import = "plugins.lsp" },
  { import = "plugins.completion" },
  -- ... more imports
}
```

## Basic Configuration

`lua/config/options.lua`:

```lua
local opt = vim.opt

-- UI
opt.number = true
opt.relativenumber = true
opt.signcolumn = "yes"
opt.cursorline = true
opt.termguicolors = true

-- Editing
opt.tabstop = 2
opt.shiftwidth = 2
opt.expandtab = true
opt.smartindent = true

-- Search
opt.ignorecase = true
opt.smartcase = true
opt.hlsearch = true

-- Split windows
opt.splitright = true
opt.splitbelow = true

-- Performance
opt.updatetime = 250
opt.timeoutlen = 300

-- Undo/Backup
opt.undofile = true
opt.undodir = vim.fn.stdpath("data") .. "/undo"
opt.backup = false
opt.swapfile = false

-- Clipboard
opt.clipboard = "unnamedplus"

-- Completion
opt.completeopt = "menu,menuone,noselect"
```

`lua/config/keymaps.lua`:

```lua
local map = vim.keymap.set

-- Better window navigation
map("n", "<C-h>", "<C-w>h")
map("n", "<C-j>", "<C-w>j")
map("n", "<C-k>", "<C-w>k")
map("n", "<C-l>", "<C-w>l")

-- Resize windows
map("n", "<C-Up>", ":resize +2<CR>")
map("n", "<C-Down>", ":resize -2<CR>")
map("n", "<C-Left>", ":vertical resize -2<CR>")
map("n", "<C-Right>", ":vertical resize +2<CR>")

-- Buffer navigation
map("n", "<S-l>", ":bnext<CR>")
map("n", "<S-h>", ":bprevious<CR>")

-- Better indenting
map("v", "<", "<gv")
map("v", ">", ">gv")

-- Move text up and down
map("v", "J", ":m '>+1<CR>gv=gv")
map("v", "K", ":m '<-2<CR>gv=gv")

-- Stay in visual mode while pasting
map("v", "p", '"_dP')

-- Clear search highlighting
map("n", "<Esc>", ":noh<CR>")

-- File operations
map("n", "<leader>w", ":w<CR>")
map("n", "<leader>q", ":q<CR>")
map("n", "<leader>Q", ":qa!<CR>")
```

## Essential Plugins

Add to `lua/plugins/essentials.lua`:

```lua
return {
  -- Dependency for many plugins
  { "nvim-lua/plenary.nvim" },

  -- Icons
  { "nvim-tree/nvim-web-devicons" },

  -- Colorscheme
  {
    "folke/tokyonight.nvim",
    priority = 1000,
    config = function()
      vim.cmd([[colorscheme tokyonight-night]])
    end,
  },

  -- Status line
  {
    "nvim-lualine/lualine.nvim",
    opts = {
      options = {
        theme = "tokyonight",
        component_separators = "|",
        section_separators = "",
      },
    },
  },

  -- File explorer
  {
    "nvim-tree/nvim-tree.lua",
    keys = {
      { "<leader>e", "<cmd>NvimTreeToggle<cr>", desc = "File Explorer" },
    },
    opts = {
      view = { width = 30 },
      renderer = {
        group_empty = true,
      },
    },
  },

  -- Fuzzy finder
  {
    "nvim-telescope/telescope.nvim",
    cmd = "Telescope",
    keys = {
      { "<leader>ff", "<cmd>Telescope find_files<cr>", desc = "Find Files" },
      { "<leader>fg", "<cmd>Telescope live_grep<cr>", desc = "Live Grep" },
      { "<leader>fb", "<cmd>Telescope buffers<cr>", desc = "Buffers" },
      { "<leader>fh", "<cmd>Telescope help_tags<cr>", desc = "Help" },
    },
    dependencies = {
      { "nvim-telescope/telescope-fzf-native.nvim", build = "make" },
    },
    config = function()
      require("telescope").setup({
        extensions = {
          fzf = {
            fuzzy = true,
            override_generic_sorter = true,
            override_file_sorter = true,
          },
        },
      })
      require("telescope").load_extension("fzf")
    end,
  },

  -- Git integration
  {
    "lewis6991/gitsigns.nvim",
    event = { "BufReadPre", "BufNewFile" },
    opts = {
      signs = {
        add = { text = "│" },
        change = { text = "│" },
        delete = { text = "_" },
        topdelete = { text = "‾" },
        changedelete = { text = "~" },
        untracked = { text = "┆" },
      },
    },
  },

  -- Which-key (shows keybindings)
  {
    "folke/which-key.nvim",
    event = "VeryLazy",
    config = function()
      require("which-key").setup()
    end,
  },

  -- Auto pairs
  {
    "windwp/nvim-autopairs",
    event = "InsertEnter",
    opts = {},
  },

  -- Comment plugin
  {
    "numToStr/Comment.nvim",
    keys = {
      { "gcc", mode = "n", desc = "Comment toggle current line" },
      { "gc", mode = { "n", "o" }, desc = "Comment toggle linewise" },
      { "gc", mode = "x", desc = "Comment toggle linewise (visual)" },
      { "gbc", mode = "n", desc = "Comment toggle current block" },
      { "gb", mode = { "n", "o" }, desc = "Comment toggle blockwise" },
      { "gb", mode = "x", desc = "Comment toggle blockwise (visual)" },
    },
    opts = {},
  },

  -- Indentation guides
  {
    "lukas-reineke/indent-blankline.nvim",
    event = { "BufReadPost", "BufNewFile" },
    main = "ibl",
    opts = {
      indent = {
        char = "│",
      },
    },
  },
}
```

## Lazy.nvim Commands

### In Neovim

```vim
:Lazy          " Open plugin manager UI
:Lazy sync     " Install, update, and clean plugins
:Lazy update   " Update plugins
:Lazy clean    " Remove unused plugins
:Lazy check    " Check for updates
:Lazy log      " Show recent updates
:Lazy restore  " Restore plugins from lockfile
:Lazy profile  " Profile plugin load times
```

## Plugin Specification Format

```lua
{
  "username/repo-name",

  -- Lazy loading
  lazy = true,                           -- Don't load on startup
  event = "VeryLazy",                   -- Load on specific events
  cmd = "CommandName",                  -- Load on command
  ft = "python",                        -- Load on filetype
  keys = {                              -- Load on key press
    { "<leader>f", "<cmd>Format<cr>" },
  },

  -- Dependencies
  dependencies = {
    "other/plugin",
  },

  -- Build step
  build = "make",

  -- Configuration
  opts = {                              -- Automatically calls setup()
    -- Plugin options
  },
  config = function()                   -- Manual setup
    require("plugin").setup({})
  end,

  -- Version/branch
  version = "1.0.0",
  branch = "main",
  tag = "v1.0",

  -- Priority
  priority = 1000,                      -- Load order (higher = earlier)

  -- Conditional loading
  cond = function()
    return vim.fn.executable("rg") == 1
  end,

  -- Initialization
  init = function()
    -- Runs before plugin is loaded
  end,
}
```

## Troubleshooting

### Plugin not loading

```vim
:Lazy load plugin-name
```

### Check load time

```vim
:Lazy profile
```

### Clear cache

```bash
rm -rf ~/.local/share/nvim/lazy
```

### Lockfile conflicts

```bash
rm ~/.config/nvim/lazy-lock.json
# Then in Neovim:
:Lazy restore
```

## Next Steps

1. ✅ Plugin Manager Setup
2. 🔧 [Configure LSP](./03-lsp-setup.md)
3. 🌳 [Setup Treesitter](./04-treesitter.md)
