# MERN Stack Development Setup

## Overview

Complete Neovim configuration for MongoDB, Express.js, React, and Node.js development.

## LSP Servers

Install via Mason (`:Mason`):

- `ts_ls` - TypeScript/JavaScript
- `eslint` - ESLint
- `html` - HTML
- `cssls` - CSS/SCSS
- `tailwindcss` - Tailwind CSS
- `emmet_ls` - Emmet abbreviations
- `jsonls` - JSON

## React/TypeScript Configuration

```lua
-- lua/plugins/react.lua
return {
  -- Enhanced TypeScript support
  {
    "pmizio/typescript-tools.nvim",
    dependencies = { "nvim-lua/plenary.nvim", "neovim/nvim-lspconfig" },
    ft = { "typescript", "typescriptreact", "javascript", "javascriptreact" },
    opts = {
      settings = {
        tsserver_file_preferences = {
          includeInlayParameterNameHints = "all",
          includeInlayParameterNameHintsWhenArgumentMatchesName = false,
          includeInlayFunctionParameterTypeHints = true,
          includeInlayVariableTypeHints = true,
          includeInlayVariableTypeHintsWhenTypeMatchesName = false,
          includeInlayPropertyDeclarationTypeHints = true,
          includeInlayFunctionLikeReturnTypeHints = true,
          includeInlayEnumMemberValueHints = true,
        },
      },
    },
  },

  -- Auto close/rename HTML tags
  {
    "windwp/nvim-ts-autotag",
    event = { "BufReadPre", "BufNewFile" },
    opts = {},
  },

  -- Tailwind CSS colorizer
  {
    "NvChad/nvim-colorizer.lua",
    event = { "BufReadPre", "BufNewFile" },
    opts = {
      user_default_options = {
        tailwind = true,
        mode = "background",
      },
    },
  },
}
```

## Node.js Package Management

```lua
-- lua/plugins/node.lua
return {
  -- Package.json manager
  {
    "vuki656/package-info.nvim",
    ft = "json",
    dependencies = { "MunifTanjim/nui.nvim" },
    opts = {},
    keys = {
      { "<leader>ns", "<cmd>lua require('package-info').show()<cr>", desc = "Show package info" },
      { "<leader>nu", "<cmd>lua require('package-info').update()<cr>", desc = "Update package" },
      { "<leader>nd", "<cmd>lua require('package-info').delete()<cr>", desc = "Delete package" },
      { "<leader>ni", "<cmd>lua require('package-info').install()<cr>", desc = "Install package" },
    },
  },
}
```

## MongoDB Support

```lua
-- lua/plugins/mongodb.lua
return {
  -- MongoDB syntax highlighting
  {
    "kongo2002/vim-mongo",
    ft = { "javascript", "typescript" },
  },
}
```

## ESLint & Prettier Setup

### Install Tools

```bash
# Via Mason
:MasonInstall eslint_d prettierd

# Or globally
npm install -g eslint_d @fsouza/prettierd
```

### Configure Formatting

```lua
-- lua/plugins/formatting.lua (update)
formatters_by_ft = {
  javascript = { "prettierd", "prettier" },
  typescript = { "prettierd", "prettier" },
  javascriptreact = { "prettierd", "prettier" },
  typescriptreact = { "prettierd", "prettier" },
  json = { "prettierd", "prettier" },
  css = { "prettierd", "prettier" },
  scss = { "prettierd", "prettier" },
  html = { "prettierd", "prettier" },
}
```

## Keybindings for MERN Development

```lua
-- lua/config/keymaps.lua

-- Run scripts
vim.keymap.set("n", "<leader>nr", ":!npm run<Space>", { desc = "Run npm script" })
vim.keymap.set("n", "<leader>nd", ":!npm run dev<CR>", { desc = "npm run dev" })
vim.keymap.set("n", "<leader>nb", ":!npm run build<CR>", { desc = "npm run build" })
vim.keymap.set("n", "<leader>nt", ":!npm test<CR>", { desc = "npm test" })

-- Package management
vim.keymap.set("n", "<leader>ni", ":!npm install<CR>", { desc = "npm install" })
vim.keymap.set("n", "<leader>nu", ":!npm update<CR>", { desc = "npm update" })
```

## Project Structure Support

```lua
-- .nvim.lua in project root (auto-loaded)
vim.opt.tabstop = 2
vim.opt.shiftwidth = 2

-- Set Node path
vim.env.PATH = vim.fn.getcwd() .. "/node_modules/.bin:" .. vim.env.PATH

-- Project-specific keymaps
vim.keymap.set("n", "<leader>r", ":!npm run dev<CR>")
```

## React Snippets

```lua
-- lua/plugins/snippets.lua
return {
  {
    "L3MON4D3/LuaSnip",
    dependencies = {
      "rafamadriz/friendly-snippets",
    },
    config = function()
      require("luasnip.loaders.from_vscode").lazy_load()

      -- Custom React snippets
      local ls = require("luasnip")
      local s = ls.snippet
      local t = ls.text_node
      local i = ls.insert_node

      ls.add_snippets("typescriptreact", {
        s("rfc", {
          t({"import React from 'react';", "", ""}),
          t("interface "), i(1, "Props"), t({" {", "  "}),
          i(2, "// props"),
          t({"", "}", "", ""}),
          t("const "), i(3, "Component"), t(": React.FC<"), i(4, "Props"), t({"> = ({}) => {", "  "}),
          t("return ("), i(5, "<div></div>"), t({");", "};", "", "export default "}), i(6, "Component"), t(";"),
        }),
      })
    end,
  },
}
```

## Testing Integration

```lua
-- lua/plugins/testing.lua
return {
  {
    "nvim-neotest/neotest",
    dependencies = {
      "nvim-neotest/nvim-nio",
      "nvim-neotest/neotest-jest",
      "nvim-neotest/neotest-vitest",
    },
    keys = {
      { "<leader>tt", "<cmd>lua require('neotest').run.run()<cr>", desc = "Run nearest test" },
      { "<leader>tf", "<cmd>lua require('neotest').run.run(vim.fn.expand('%'))<cr>", desc = "Run file tests" },
      { "<leader>ts", "<cmd>lua require('neotest').summary.toggle()<cr>", desc = "Toggle test summary" },
    },
    config = function()
      require("neotest").setup({
        adapters = {
          require("neotest-jest")({
            jestCommand = "npm test --",
          }),
          require("neotest-vitest"),
        },
      })
    end,
  },
}
```

## Recommended File Tree

```bash
project/
├── .nvim.lua               # Project-specific config
├── .eslintrc.js
├── .prettierrc
├── tsconfig.json
├── package.json
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── services/
│   ├── utils/
│   └── App.tsx
└── server/                 # Express backend
    ├── controllers/
    ├── models/
    ├── routes/
    └── server.ts
```

## Common Workflows

### Component Development

1. Open component: `<leader>ff` → type filename
2. Live edit with hot reload
3. Format on save: Auto with conform.nvim
4. Test: `<leader>tt` for nearest test

### API Development

1. Edit Express routes in split
2. Test with REST client or Postman
3. Auto-format with Prettier
4. Lint with ESLint

## Next Steps

- [Python Development](./07-python-setup.md)
- [Debugging Setup](./16-debugging.md)
- [Testing Integration](./17-testing.md)
