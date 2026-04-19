# TypeScript & JavaScript Development

## Overview

This guide covers setting up Neovim as a full TypeScript/JavaScript IDE covering:

- **ts_ls** — TypeScript Language Server (LSP)
- **ESLint** — Linting with auto-fix
- **Prettier** — Opinionated formatter
- **React / JSX / TSX** — JSX-aware tooling
- **Import management** — Auto-imports, unused import removal
- **Testing** — Jest integration via Neotest

---

## LSP: TypeScript Language Server

### Plugin Setup

```lua
-- lua/plugins/typescript.lua
return {
  -- Official TypeScript LSP integration
  {
    "pmizio/typescript-tools.nvim",
    dependencies = { "nvim-lua/plenary.nvim", "neovim/nvim-lspconfig" },
    ft = { "javascript", "javascriptreact", "typescript", "typescriptreact" },
    opts = {
      settings = {
        -- Publish diagnostics separately for each tool
        separate_diagnostic_server = true,
        publish_diagnostic_on = "insert_leave",

        -- Inlay hints (requires Neovim 0.10+)
        tsserver_file_preferences = {
          includeInlayParameterNameHints         = "all",
          includeInlayParameterNameHintsWhenArgumentMatchesName = false,
          includeInlayFunctionParameterTypeHints = true,
          includeInlayVariableTypeHints          = true,
          includeInlayVariableTypeHintsWhenTypeMatchesName = false,
          includeInlayPropertyDeclarationTypeHints = true,
          includeInlayFunctionLikeReturnTypeHints  = true,
          includeInlayEnumMemberValueHints         = true,
        },

        -- Code lens (show reference counts above functions)
        tsserver_plugins = {},
      },
    },
  },
}
```

### Alternative: Use mason-lspconfig with ts_ls

If you prefer the standard approach:

```lua
-- In your mason-lspconfig setup_handlers:
["ts_ls"] = function()
  lspconfig.ts_ls.setup({
    capabilities = capabilities,
    settings = {
      typescript = {
        inlayHints = {
          includeInlayParameterNameHints         = "all",
          includeInlayVariableTypeHints          = true,
          includeInlayFunctionLikeReturnTypeHints = true,
        },
        suggest = {
          includeCompletionsForModuleExports = true,
        },
      },
      javascript = {
        inlayHints = {
          includeInlayParameterNameHints = "literals",
        },
      },
    },
    on_attach = function(client, bufnr)
      -- Disable formatting in favour of Prettier
      client.server_capabilities.documentFormattingProvider = false
      client.server_capabilities.documentRangeFormattingProvider = false
    end,
  })
end,
```

---

## ESLint

### Plugin Configuration

```lua
-- In mason-lspconfig ensure_installed:
"eslint",

-- In setup_handlers:
["eslint"] = function()
  lspconfig.eslint.setup({
    capabilities = capabilities,
    settings = {
      workingDirectory = { mode = "auto" },
      format           = { enable = true },
      lint             = { enable = true },
      packageManager   = "npm",
    },
    on_attach = function(client, bufnr)
      -- Auto-fix on save
      vim.api.nvim_create_autocmd("BufWritePre", {
        buffer   = bufnr,
        command  = "EslintFixAll",
      })
    end,
  })
end,
```

### Project .eslintrc.json (Modern Flat Config)

```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "plugins": ["@typescript-eslint", "react", "react-hooks"],
  "rules": {
    "@typescript-eslint/no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/no-explicit-any": "warn",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

---

## Prettier (Formatting)

### conform.nvim configuration

```lua
-- In your conform.nvim opts:
formatters_by_ft = {
  javascript      = { "prettier" },
  typescript      = { "prettier" },
  javascriptreact = { "prettier" },
  typescriptreact = { "prettier" },
  css             = { "prettier" },
  scss            = { "prettier" },
  html            = { "prettier" },
  json            = { "prettier" },
  jsonc           = { "prettier" },
  yaml            = { "prettier" },
  markdown        = { "prettier" },
  graphql         = { "prettier" },
},
```

### Project .prettierrc

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "always"
}
```

---

## Treesitter Parsers for JS/TS

Ensure these are installed:

```lua
ensure_installed = {
  "javascript",
  "typescript",
  "tsx",           -- TypeScript JSX
  "json",
  "html",
  "css",
  "graphql",
},
```

---

## Auto-Close HTML/JSX Tags

```lua
-- Already included via nvim-ts-autotag in treesitter config
-- Supports: html, xml, jsx, tsx, vue, svelte, php, markdown
{ "windwp/nvim-ts-autotag", opts = {} }
```

---

## Import Sorting & Management

### Using typescript-tools commands

```vim
:TSToolsOrganizeImports      " Sort and remove unused imports
:TSToolsAddMissingImports    " Add missing imports automatically
:TSToolsFixAll               " Fix all fixable issues
:TSToolsRenameFile           " Rename file and update all imports
:TSToolsGoToSourceDefinition " Go to source (not .d.ts)
```

Keymap suggestions:

```lua
vim.keymap.set("n", "<leader>oi", "<cmd>TSToolsOrganizeImports<CR>",   { desc = "Organize imports" })
vim.keymap.set("n", "<leader>am", "<cmd>TSToolsAddMissingImports<CR>", { desc = "Add missing imports" })
vim.keymap.set("n", "<leader>rf", "<cmd>TSToolsRenameFile<CR>",        { desc = "Rename file (update imports)" })
```

---

## Type Checking Workflow

Enable strict TypeScript checking per project in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

Run full type check without opening Neovim:

```bash
npx tsc --noEmit
```

---

## Useful Keymaps Reference

| Keymap        | Action                             |
|---------------|------------------------------------|
| `gd`          | Go to definition                   |
| `gD`          | Go to declaration                  |
| `gi`          | Go to implementation               |
| `gr`          | Find all references                |
| `K`           | Hover type information             |
| `<leader>rn`  | Rename symbol                      |
| `<leader>ca`  | Code actions (import fix, etc.)    |
| `<leader>f`   | Format buffer with Prettier        |
| `<leader>oi`  | Organize imports                   |
| `<leader>am`  | Add missing imports                |

---

## Troubleshooting

### TypeScript server keeps crashing

```bash
# Check Node.js version (ts_ls needs >= 18)
node --version

# Increase memory limit for large projects
# In LSP settings:
init_options = {
  maxTsServerMemory = 4096,  -- MB
}
```

### Inlay hints not showing

```lua
-- Requires Neovim >= 0.10 and is off by default
vim.lsp.inlay_hint.enable(true)
-- Toggle:
vim.keymap.set("n", "<leader>ih", function()
  vim.lsp.inlay_hint.enable(not vim.lsp.inlay_hint.is_enabled())
end, { desc = "Toggle inlay hints" })
```

### JSX not recognized as TSX

Ensure the buffer filetype is detected correctly:

```lua
vim.filetype.add({
  extension = {
    jsx = "javascriptreact",
    tsx = "typescriptreact",
  },
})
```

---

## Next Steps

1. [SQL Databases](./09-sql-databases.md)
2. [NoSQL Databases](./10-nosql-databases.md)
3. [Debugging](./16-debugging.md)
