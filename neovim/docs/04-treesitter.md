# Treesitter Configuration

## What is Treesitter?

Treesitter is a parser generator tool that builds concrete syntax trees for source
files and keeps them up to date as you edit. In Neovim it powers:

- **Syntax highlighting** — semantic, not regex-based
- **Text objects** — select/delete/change functions, classes, blocks
- **Incremental selection** — expand/contract selection by node
- **Indentation** — context-aware smart indent
- **Folding** — fold by syntax node
- **Navigation** — jump between functions, classes, etc.

---

## Installation

```lua
-- lua/plugins/treesitter.lua
return {
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    event = { "BufReadPre", "BufNewFile" },
    dependencies = {
      "nvim-treesitter/nvim-treesitter-textobjects", -- text objects
      "nvim-treesitter/nvim-treesitter-context",      -- sticky function header
      "windwp/nvim-ts-autotag",                       -- auto-close HTML tags
      "JoosepAlviste/nvim-ts-context-commentstring",  -- context-aware comments
    },
    config = function()
      require("nvim-treesitter.configs").setup({

        -- Install parsers automatically
        ensure_installed = {
          -- General
          "bash", "lua", "vim", "vimdoc", "regex", "markdown", "markdown_inline",
          -- Web
          "html", "css", "javascript", "typescript", "tsx", "json", "jsonc", "yaml",
          -- Python
          "python",
          -- DevOps
          "dockerfile", "terraform", "hcl", "toml",
          -- Databases
          "sql",
          -- Go / Rust (optional)
          "go", "rust",
          -- Git
          "git_config", "gitcommit", "gitignore",
        },

        -- Install parsers synchronously (only applied to `ensure_installed`)
        sync_install = false,

        -- Automatically install missing parsers when entering buffer
        auto_install = true,

        highlight = {
          enable = true,
          -- Disable for very large files
          disable = function(lang, buf)
            local max_filesize = 500 * 1024 -- 500 KB
            local ok, stats = pcall(vim.loop.fs_stat, vim.api.nvim_buf_get_name(buf))
            if ok and stats and stats.size > max_filesize then
              return true
            end
          end,
          -- Use vim regex highlighting as fallback for some languages
          additional_vim_regex_highlighting = { "ruby" },
        },

        indent = {
          enable = true,
          -- Disable for languages with broken indent rules
          disable = { "yaml" },
        },

        -- Incremental selection
        incremental_selection = {
          enable = true,
          keymaps = {
            init_selection    = "<C-space>",
            node_incremental  = "<C-space>",
            scope_incremental = "<C-s>",
            node_decremental  = "<M-space>",
          },
        },

        -- Text objects (requires nvim-treesitter-textobjects)
        textobjects = {
          select = {
            enable = true,
            lookahead = true, -- Jump to next text object if not currently on one
            keymaps = {
              ["af"] = "@function.outer",
              ["if"] = "@function.inner",
              ["ac"] = "@class.outer",
              ["ic"] = "@class.inner",
              ["aa"] = "@parameter.outer",
              ["ia"] = "@parameter.inner",
              ["ab"] = "@block.outer",
              ["ib"] = "@block.inner",
              ["al"] = "@loop.outer",
              ["il"] = "@loop.inner",
              ["ai"] = "@conditional.outer",
              ["ii"] = "@conditional.inner",
            },
          },

          move = {
            enable = true,
            set_jumps = true, -- set jumps in the jumplist
            goto_next_start = {
              ["]f"] = "@function.outer",
              ["]c"] = "@class.outer",
              ["]a"] = "@parameter.inner",
            },
            goto_next_end = {
              ["]F"] = "@function.outer",
              ["]C"] = "@class.outer",
            },
            goto_previous_start = {
              ["[f"] = "@function.outer",
              ["[c"] = "@class.outer",
              ["[a"] = "@parameter.inner",
            },
            goto_previous_end = {
              ["[F"] = "@function.outer",
              ["[C"] = "@class.outer",
            },
          },

          swap = {
            enable = true,
            swap_next     = { ["<leader>a"] = "@parameter.inner" },
            swap_previous = { ["<leader>A"] = "@parameter.inner" },
          },

          peek_definition_code = {
            ["<leader>df"] = "@function.outer",
            ["<leader>dF"] = "@class.outer",
          },
        },

        -- Auto-close and rename HTML tags
        autotag = { enable = true },
      })
    end,
  },

  -- Sticky function/class header at the top of the window
  {
    "nvim-treesitter/nvim-treesitter-context",
    opts = {
      enable = true,
      max_lines = 3,
      min_window_height = 0,
      line_numbers = true,
      multiline_threshold = 20,
      trim_scope = "outer",
      mode = "cursor",
    },
  },
}
```

---

## Language Parsers

Install additional parsers manually:

```vim
:TSInstall <language>
:TSInstall python typescript go rust
```

List available parsers:

```vim
:TSInstallInfo
```

List installed parsers:

```vim
:TSModuleInfo
```

Update all parsers:

```vim
:TSUpdate
```

### Common Parsers Reference

| Language   | Parser Name      | Notes                      |
|------------|-----------------|----------------------------|
| Python     | `python`        | Full support               |
| JavaScript | `javascript`    | Includes JSX               |
| TypeScript | `typescript`    | TS only                    |
| TSX        | `tsx`           | TypeScript + JSX           |
| Lua        | `lua`           | Essential for config       |
| Bash       | `bash`          | Shell scripting            |
| SQL        | `sql`           |                            |
| Docker     | `dockerfile`    |                            |
| Terraform  | `terraform`     | + `hcl`                    |
| YAML       | `yaml`          |                            |
| JSON       | `json`          |                            |
| Markdown   | `markdown`      | + `markdown_inline`        |

---

## Treesitter-Context (Sticky Header)

Shows the current function/class signature at the top of the window while scrolling through long files.

```lua
-- Toggle context on/off
vim.keymap.set("n", "<leader>tc", "<cmd>TSContextToggle<CR>", { desc = "Toggle treesitter context" })
```

---

## Folding with Treesitter

Add to `lua/config/options.lua`:

```lua
-- Use treesitter for folding
vim.opt.foldmethod = "expr"
vim.opt.foldexpr   = "nvim_treesitter#foldexpr()"
vim.opt.foldlevel  = 99   -- Open all folds by default
vim.opt.foldenable = true
```

Fold keymaps (built-in Vim):

| Key   | Action                    |
|-------|---------------------------|
| `zc`  | Close fold                |
| `zo`  | Open fold                 |
| `za`  | Toggle fold               |
| `zM`  | Close all folds           |
| `zR`  | Open all folds            |
| `zj`  | Move to next fold         |
| `zk`  | Move to previous fold     |

---

## Playground (Interactive Inspection)

Install the playground plugin to inspect syntax trees:

```lua
{ "nvim-treesitter/playground", cmd = "TSPlaygroundToggle" }
```

```vim
:TSPlaygroundToggle   " Open the syntax tree inspector
:TSHighlightCapturesUnderCursor  " Show highlight groups at cursor
```

---

## Troubleshooting

### Parser not available

```vim
:TSInstallInfo   " Check if parser name is correct
:checkhealth nvim-treesitter
```

### Highlighting broken or wrong

```vim
-- Disable and re-enable for current buffer
:TSBufDisable highlight
:TSBufEnable highlight

-- Check highlight captures under cursor
:TSHighlightCapturesUnderCursor
```

### Parser fails to compile

```bash
# Ensure C compiler is installed
gcc --version
clang --version

# Arch
sudo pacman -S base-devel

# Ubuntu
sudo apt install build-essential
```

---

## Next Steps

1. [Configure Autocompletion](./05-completion.md)
2. [MERN Stack Setup](./06-mern-stack.md)
