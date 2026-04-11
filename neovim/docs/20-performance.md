# Performance Optimization

## Overview

A fast Neovim startup and smooth editing experience require intentional tuning.
This guide covers:

- Startup time profiling and reduction
- Lazy-loading strategies
- Large file handling
- LSP performance tuning
- Treesitter performance
- Memory management

---

## Measuring Startup Time

```bash
# Basic startup measurement
nvim --startuptime /tmp/nvim-startup.log +q && sort -k2 -n /tmp/nvim-startup.log | tail -20

# Compare before/after changes
hyperfine --warmup 3 'nvim --headless +q'
```

### Inside Neovim

```vim
:Lazy profile    " lazy.nvim profiler (shows per-plugin load time)
```

---

## Lazy-Loading Strategies

The single biggest win is loading plugins only when needed.

```lua
-- lua/plugins/example.lua
return {
  -- ── Load on specific commands ─────────────────────────────────────
  {
    "tpope/vim-fugitive",
    cmd = { "Git", "G" },            -- only load when :Git is run
  },

  -- ── Load on filetype ──────────────────────────────────────────────
  {
    "nvim-neotest/neotest",
    ft = { "python", "javascript", "typescript", "go" },
  },

  -- ── Load on keybinding ────────────────────────────────────────────
  {
    "kdheepak/lazygit.nvim",
    keys = { "<leader>gg" },         -- only load when keymap is pressed
  },

  -- ── Load after UI renders (safe for most UI plugins) ─────────────
  {
    "folke/which-key.nvim",
    event = "VeryLazy",
  },

  -- ── Load on buffer open (for syntax / LSP plugins) ───────────────
  {
    "nvim-treesitter/nvim-treesitter",
    event = { "BufReadPre", "BufNewFile" },
  },

  -- ── Defer non-essential plugins ───────────────────────────────────
  {
    "nvimdev/dashboard-nvim",
    event = "VimEnter",
  },
}
```

### Events Reference

| Event            | When it fires                                |
|-----------------|----------------------------------------------|
| `VimEnter`       | After all startup processing                 |
| `VeryLazy`       | After `VimEnter`, ideal for UI enhancements  |
| `BufReadPre`     | Before reading a buffer — for syntax/LSP     |
| `BufNewFile`     | When opening a new (empty) buffer            |
| `InsertEnter`    | When entering insert mode                    |
| `CmdlineEnter`   | When entering command-line mode              |

---

## Disable Built-in Plugins You Don't Need

```lua
-- In your lazy.nvim setup options:
require("lazy").setup(plugins, {
  performance = {
    rtp = {
      disabled_plugins = {
        "gzip",           -- .gz file support
        "matchit",        -- extended % matching (use treesitter instead)
        "matchparen",     -- highlight matching parens (treesitter does this)
        "netrwPlugin",    -- built-in file explorer (use neo-tree/oil)
        "tarPlugin",
        "tohtml",
        "tutor",
        "zipPlugin",
        "rplugin",        -- only needed for some Python plugins
        "shada",          -- set shada options separately if needed
      },
    },
  },
})
```

---

## Large File Handling

Files over 500KB cause severe slowdowns with syntax highlighting and LSP.
Detect and handle them separately:

```lua
-- lua/config/autocmds.lua
local large_file_group = vim.api.nvim_create_augroup("LargeFile", { clear = true })

vim.api.nvim_create_autocmd("BufReadPre", {
  group    = large_file_group,
  pattern  = "*",
  callback = function(args)
    local size = vim.fn.getfsize(args.match)
    if size > 500 * 1024 then  -- 500 KB
      vim.notify("Large file: disabling heavy features", vim.log.levels.WARN)

      -- Treesitter
      vim.cmd("TSBufDisable highlight")
      vim.cmd("TSBufDisable indent")
      vim.cmd("TSBufDisable incremental_selection")

      -- Syntax (fall back to regex)
      vim.bo[args.buf].syntax = "OFF"

      -- LSP
      vim.schedule(function()
        for _, client in ipairs(vim.lsp.get_active_clients({ bufnr = args.buf })) do
          vim.lsp.buf_detach_client(args.buf, client.id)
        end
      end)

      -- Undo history
      vim.bo[args.buf].undofile  = false
      vim.bo[args.buf].swapfile  = false
      vim.bo[args.buf].undolevels = -1

      -- Line numbers (expensive for huge files)
      vim.wo.foldmethod    = "manual"
      vim.wo.spell         = false
      vim.wo.relativenumber = false
    end
  end,
})
```

---

## LSP Performance

### Reduce diagnostic update frequency

```lua
vim.lsp.handlers["textDocument/publishDiagnostics"] = vim.lsp.with(
  vim.lsp.diagnostic.on_publish_diagnostics,
  {
    update_in_insert = false,   -- don't update while typing
    severity_sort    = true,
  }
)

-- Or via diagnostic config:
vim.diagnostic.config({
  update_in_insert = false,
  virtual_text     = { spacing = 4, prefix = "●" },
})
```

### Throttle LSP progress notifications

```lua
-- Reduce notify spam for long-running LSP tasks:
local notify = vim.notify
vim.notify = function(msg, ...)
  if msg:find("Loading Pyright") or msg:find("indexing") then return end
  notify(msg, ...)
end
```

### TypeScript: increase memory for large repos

```lua
lspconfig.ts_ls.setup({
  init_options = {
    maxTsServerMemory = 4096,  -- MB (default is 3072)
  },
})
```

### Pyright: exclude unnecessary paths

```json
// pyrightconfig.json in project root
{
  "exclude": [
    "**/node_modules",
    "**/__pycache__",
    ".venv",
    "dist",
    "build"
  ],
  "pythonVersion": "3.12",
  "typeCheckingMode": "basic"
}
```

---

## Treesitter Performance

```lua
-- Disable slow parsers for certain conditions
highlight = {
  enable  = true,
  disable = function(lang, buf)
    -- Disable for large files
    local max_filesize = 500 * 1024  -- 500 KB
    local ok, stats = pcall(vim.loop.fs_stat, vim.api.nvim_buf_get_name(buf))
    if ok and stats and stats.size > max_filesize then return true end

    -- Disable for specific languages that are slow
    local slow_parsers = { "markdown" }
    return vim.tbl_contains(slow_parsers, lang)
  end,
  additional_vim_regex_highlighting = false,  -- disable regex fallback
},
```

---

## Startup Optimisations

### defer_fn for non-critical init

```lua
-- Run heavy setup after Neovim is fully loaded
vim.defer_fn(function()
  require("nvim-treesitter.configs").setup({ ... })
end, 0)
```

### Cache Lua modules (impatient pattern — now built-in)

Neovim 0.9+ includes `vim.loader` which caches Lua bytecode automatically:

```lua
-- In init.lua, before any require():
vim.loader.enable()
```

### Profile individual plugin load

```lua
-- Check how long a specific module takes to load
local start = vim.loop.hrtime()
require("telescope")
local ms = (vim.loop.hrtime() - start) / 1e6
print(("telescope loaded in %.2fms"):format(ms))
```

---

## Useful Options for Performance

```lua
-- lua/config/options.lua
vim.opt.lazyredraw     = false   -- don't use in Neovim (causes issues); use instead:
vim.opt.updatetime     = 200     -- faster CursorHold events (default 4000)
vim.opt.timeoutlen     = 300     -- faster which-key popup
vim.opt.redrawtime     = 1500    -- stop syntax highlight if it takes > 1.5s
vim.opt.maxmempattern  = 2000    -- max memory for pattern matching (KB)

-- Decrease shell startup overhead for terminal buffers
vim.opt.shell         = "bash"  -- use bash directly; avoid exotic shells
```

---

## Benchmarks: Target Metrics

| Metric                   | Target           | Notes                              |
|--------------------------|------------------|------------------------------------|
| Cold startup time        | < 100ms          | With lazy loading                  |
| Keypress latency         | < 10ms           | Disable heavy autocmds on insert   |
| Large file (1MB) open    | < 2s             | With LSP/TS disabled               |
| LSP attach time          | < 500ms          | Depends on project size            |
| Completion popup latency | < 100ms          | With nvim-cmp + caching            |

---

## Monitoring During Use

```vim
:checkhealth          " Overall health check
:Lazy profile         " Plugin load times
:LspInfo              " LSP server status
:TSModuleInfo         " Treesitter module status
:lua print(vim.inspect(vim.lsp.get_active_clients()))
```

Watch memory:

```bash
# Monitor Neovim process memory
watch -n 1 'ps -o pid,rss,vsz,comm -p $(pgrep nvim)'
```

---

## Troubleshooting Slowdowns

### Identify the slow plugin

```bash
nvim --startuptime /tmp/s.log +q && sort -k2 -rn /tmp/s.log | head -20
```

### Identify slow autocmds

```vim
:lua vim.cmd("redir >> /tmp/autocmds.txt | silent autocmd | redir END")
```

### Check for excessive CursorMoved autocmds

```lua
-- Find all CursorMoved listeners (common culprit):
for _, au in ipairs(vim.api.nvim_get_autocmds({ event = "CursorMoved" })) do
  print(au.desc or au.callback)
end
```

---

## Next Steps

- Review the [complete plugin list](./02-plugin-manager.md) for lazy-loading opportunities
- Profile with `:Lazy profile` after every major config change
