# LSP Configuration

## Overview

Language Server Protocol (LSP) provides IDE-like features:

- Auto-completion
- Go-to-definition
- Hover documentation
- Error diagnostics
- Code actions & refactoring
- Find references

## Core Plugins

```lua
-- lua/plugins/lsp.lua
return {
  -- LSP Configuration
  {
    "neovim/nvim-lspconfig",
    event = { "BufReadPre", "BufNewFile" },
    dependencies = {
      "hrsh7th/cmp-nvim-lsp",
      { "folke/neodev.nvim", opts = {} },
    },
  },

  -- Package Manager for LSP servers
  {
    "williamboman/mason.nvim",
    cmd = "Mason",
    build = ":MasonUpdate",
    opts = {
      ui = {
        border = "rounded",
        icons = {
          package_installed = "✓",
          package_pending = "➜",
          package_uninstalled = "✗"
        }
      }
    },
  },

  -- Bridge between Mason and lspconfig
  {
    "williamboman/mason-lspconfig.nvim",
    dependencies = {
      "williamboman/mason.nvim",
      "neovim/nvim-lspconfig",
    },
    config = function()
      require("mason").setup()
      require("mason-lspconfig").setup({
        ensure_installed = {
          -- Web Development
          "ts_ls",          -- TypeScript/JavaScript
          "eslint",         -- ESLint
          "html",           -- HTML
          "cssls",          -- CSS
          "tailwindcss",    -- Tailwind CSS
          "emmet_ls",       -- Emmet

          -- Python
          "pyright",        -- Python (or use basedpyright)
          "ruff_lsp",       -- Python linter/formatter

          -- Lua (for Neovim config)
          "lua_ls",

          -- JSON/YAML
          "jsonls",
          "yamlls",

          -- SQL
          "sqlls",

          -- DevOps
          "dockerls",
          "docker_compose_language_service",
          "terraformls",
          "ansiblels",
        },
        automatic_installation = true,
      })

      -- Setup LSP servers
      local lspconfig = require("lspconfig")
      local capabilities = require("cmp_nvim_lsp").default_capabilities()

      -- Auto-setup servers installed via Mason
      require("mason-lspconfig").setup_handlers({
        -- Default handler
        function(server_name)
          lspconfig[server_name].setup({
            capabilities = capabilities,
          })
        end,

        -- Custom handlers for specific servers
        ["lua_ls"] = function()
          lspconfig.lua_ls.setup({
            capabilities = capabilities,
            settings = {
              Lua = {
                diagnostics = {
                  globals = { "vim" },
                },
                workspace = {
                  library = vim.api.nvim_get_runtime_file("", true),
                  checkThirdParty = false,
                },
                telemetry = { enable = false },
              },
            },
          })
        end,

        ["ts_ls"] = function()
          lspconfig.ts_ls.setup({
            capabilities = capabilities,
            settings = {
              typescript = {
                inlayHints = {
                  includeInlayParameterNameHints = "all",
                  includeInlayParameterNameHintsWhenArgumentMatchesName = false,
                  includeInlayFunctionParameterTypeHints = true,
                  includeInlayVariableTypeHints = true,
                  includeInlayPropertyDeclarationTypeHints = true,
                  includeInlayFunctionLikeReturnTypeHints = true,
                  includeInlayEnumMemberValueHints = true,
                }
              }
            }
          })
        end,

        ["pyright"] = function()
          lspconfig.pyright.setup({
            capabilities = capabilities,
            settings = {
              python = {
                analysis = {
                  typeCheckingMode = "basic",
                  autoSearchPaths = true,
                  useLibraryCodeForTypes = true,
                  diagnosticMode = "workspace",
                }
              }
            }
          })
        end,
      })
    end,
  },
}
```

## LSP Keymaps

Add to `lua/config/keymaps.lua`:

```lua
-- LSP Keymaps (set in on_attach)
vim.api.nvim_create_autocmd("LspAttach", {
  group = vim.api.nvim_create_augroup("UserLspConfig", {}),
  callback = function(ev)
    local opts = { buffer = ev.buf }

    -- Navigation
    vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
    vim.keymap.set("n", "gD", vim.lsp.buf.declaration, opts)
    vim.keymap.set("n", "gi", vim.lsp.buf.implementation, opts)
    vim.keymap.set("n", "gr", vim.lsp.buf.references, opts)
    vim.keymap.set("n", "gt", vim.lsp.buf.type_definition, opts)

    -- Documentation
    vim.keymap.set("n", "K", vim.lsp.buf.hover, opts)
    vim.keymap.set("n", "<C-k>", vim.lsp.buf.signature_help, opts)

    -- Code Actions
    vim.keymap.set("n", "<leader>ca", vim.lsp.buf.code_action, opts)
    vim.keymap.set("n", "<leader>rn", vim.lsp.buf.rename, opts)
    vim.keymap.set("n", "<leader>f", function()
      vim.lsp.buf.format({ async = true })
    end, opts)

    -- Diagnostics
    vim.keymap.set("n", "[d", vim.diagnostic.goto_prev, opts)
    vim.keymap.set("n", "]d", vim.diagnostic.goto_next, opts)
    vim.keymap.set("n", "<leader>d", vim.diagnostic.open_float, opts)
    vim.keymap.set("n", "<leader>q", vim.diagnostic.setloclist, opts)

    -- Workspace
    vim.keymap.set("n", "<leader>wa", vim.lsp.buf.add_workspace_folder, opts)
    vim.keymap.set("n", "<leader>wr", vim.lsp.buf.remove_workspace_folder, opts)
    vim.keymap.set("n", "<leader>wl", function()
      print(vim.inspect(vim.lsp.buf.list_workspace_folders()))
    end, opts)
  end,
})
```

## Diagnostic Configuration

Add to `lua/config/options.lua`:

```lua
-- Diagnostic configuration
vim.diagnostic.config({
  virtual_text = {
    prefix = "●",
    source = "if_many",
  },
  signs = true,
  underline = true,
  update_in_insert = false,
  severity_sort = true,
  float = {
    focusable = false,
    style = "minimal",
    border = "rounded",
    source = "always",
    header = "",
    prefix = "",
  },
})

-- Diagnostic signs
local signs = { Error = " ", Warn = " ", Hint = " ", Info = " " }
for type, icon in pairs(signs) do
  local hl = "DiagnosticSign" .. type
  vim.fn.sign_define(hl, { text = icon, texthl = hl, numhl = hl })
end
```

## Formatters (conform.nvim)

```lua
-- lua/plugins/formatting.lua
return {
  "stevearc/conform.nvim",
  event = { "BufReadPre", "BufNewFile" },
  keys = {
    {
      "<leader>f",
      function()
        require("conform").format({ async = true, lsp_fallback = true })
      end,
      mode = { "n", "v" },
      desc = "Format buffer",
    },
  },
  opts = {
    formatters_by_ft = {
      javascript = { "prettier" },
      typescript = { "prettier" },
      javascriptreact = { "prettier" },
      typescriptreact = { "prettier" },
      css = { "prettier" },
      html = { "prettier" },
      json = { "prettier" },
      yaml = { "prettier" },
      markdown = { "prettier" },
      lua = { "stylua" },
      python = { "ruff_format" },
      sh = { "shfmt" },
    },
    format_on_save = {
      timeout_ms = 500,
      lsp_fallback = true,
    },
  },
}
```

## Linting (nvim-lint)

```lua
-- lua/plugins/linting.lua
return {
  "mfussenegger/nvim-lint",
  event = { "BufReadPre", "BufNewFile" },
  config = function()
    local lint = require("lint")

    lint.linters_by_ft = {
      javascript = { "eslint_d" },
      typescript = { "eslint_d" },
      javascriptreact = { "eslint_d" },
      typescriptreact = { "eslint_d" },
      python = { "ruff" },
      dockerfile = { "hadolint" },
      yaml = { "yamllint" },
    }

    -- Auto-lint on save and text change
    local lint_augroup = vim.api.nvim_create_augroup("lint", { clear = true })
    vim.api.nvim_create_autocmd({ "BufEnter", "BufWritePost", "InsertLeave" }, {
      group = lint_augroup,
      callback = function()
        lint.try_lint()
      end,
    })

    vim.keymap.set("n", "<leader>l", function()
      lint.try_lint()
    end, { desc = "Trigger linting" })
  end,
}
```

## Install LSP Servers via Mason

### In Neovim

```vim
:Mason
```

Navigate and install:

- `i` - Install
- `u` - Update
- `X` - Uninstall
- `g?` - Help

### Via Command Line

```vim
:MasonInstall ts_ls pyright lua_ls
```

## Common LSP Servers

| Language              | Server      | Mason Name    |
| --------------------- | ----------- | ------------- |
| JavaScript/TypeScript | ts_ls       | `ts_ls`       |
| Python                | Pyright     | `pyright`     |
| Python                | Ruff        | `ruff_lsp`    |
| Lua                   | lua_ls      | `lua_ls`      |
| HTML                  | HTML LS     | `html`        |
| CSS                   | CSS LS      | `cssls`       |
| JSON                  | JSON LS     | `jsonls`      |
| Docker                | dockerls    | `dockerls`    |
| YAML                  | yamlls      | `yamlls`      |
| Terraform             | terraformls | `terraformls` |
| SQL                   | sqls        | `sqlls`       |

## Troubleshooting

### LSP not attaching

```vim
:LspInfo
:checkhealth lsp
```

### Server logs

```lua
vim.lsp.set_log_level("debug")
-- Then check: ~/.local/state/nvim/lsp.log
```

### Restart LSP

```vim
:LspRestart
```

### Format on save not working

Check buffer formatting:

```vim
:lua vim.lsp.buf.format({ async = false })
```

## Next Steps

1. ✅ LSP Configuration
2. 🌳 [Setup Treesitter](./04-treesitter.md)
3. 💬 [Configure Autocompletion](./05-completion.md)
