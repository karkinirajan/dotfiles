# Autocompletion Setup

## Overview

Neovim uses **nvim-cmp** as its completion engine, connected to multiple sources:

| Source              | Plugin                    | Provides                        |
|---------------------|---------------------------|---------------------------------|
| LSP                 | `cmp-nvim-lsp`           | Language-server completions     |
| Buffer words        | `cmp-buffer`             | Words in open buffers           |
| File paths          | `cmp-path`               | Filesystem paths                |
| Snippets            | `cmp_luasnip`            | LuaSnip snippet expansion       |
| Neovim API/Lua      | `cmp-nvim-lua`           | Neovim Lua API                  |
| Git commits         | `cmp-git`                | Commit hashes, authors          |
| Command-line        | `cmp-cmdline`            | `:` commands and `/` search     |

---

## Plugin Setup

```lua
-- lua/plugins/completion.lua
return {
  -- Snippet engine
  {
    "L3MON4D3/LuaSnip",
    version = "v2.*",
    build = "make install_jsregexp",  -- optional: regex support
    dependencies = {
      -- Community snippet collection (2000+ snippets)
      "rafamadriz/friendly-snippets",
    },
    config = function()
      local luasnip = require("luasnip")

      -- Load VSCode-style snippets from friendly-snippets
      require("luasnip.loaders.from_vscode").lazy_load()

      -- Load your custom snippets from ~/.config/nvim/snippets/
      require("luasnip.loaders.from_lua").lazy_load({ paths = "~/.config/nvim/snippets" })

      -- Extend filetypes (e.g. use JS snippets in TS files)
      luasnip.filetype_extend("typescript", { "javascript" })
      luasnip.filetype_extend("typescriptreact", { "typescript", "javascript" })
      luasnip.filetype_extend("javascriptreact", { "javascript" })
    end,
  },

  -- Completion engine
  {
    "hrsh7th/nvim-cmp",
    event = { "InsertEnter", "CmdlineEnter" },
    dependencies = {
      "hrsh7th/cmp-nvim-lsp",      -- LSP source
      "hrsh7th/cmp-buffer",        -- Buffer words
      "hrsh7th/cmp-path",          -- Filesystem paths
      "saadparwaiz1/cmp_luasnip",  -- Snippet integration
      "hrsh7th/cmp-nvim-lua",      -- Neovim Lua API
      "hrsh7th/cmp-cmdline",       -- Command-line completion
      "petertriho/cmp-git",        -- Git commits and issues
      "onsails/lspkind.nvim",      -- VSCode-like icons in menu
    },
    config = function()
      local cmp     = require("cmp")
      local luasnip = require("luasnip")
      local lspkind = require("lspkind")

      -- Helper: check if there is text before the cursor
      local has_words_before = function()
        local line, col = unpack(vim.api.nvim_win_get_cursor(0))
        return col ~= 0
          and vim.api.nvim_buf_get_lines(0, line - 1, line, true)[1]:sub(col, col):match("%s") == nil
      end

      cmp.setup({
        -- ── Snippet expansion ─────────────────────────────────────────────
        snippet = {
          expand = function(args)
            luasnip.lsp_expand(args.body)
          end,
        },

        -- ── Window appearance ─────────────────────────────────────────────
        window = {
          completion    = cmp.config.window.bordered(),
          documentation = cmp.config.window.bordered(),
        },

        -- ── Completion behaviour ──────────────────────────────────────────
        completion = {
          completeopt = "menu,menuone,noinsert",
        },

        -- ── Key mappings ──────────────────────────────────────────────────
        mapping = cmp.mapping.preset.insert({
          -- Navigate the completion list
          ["<C-n>"]   = cmp.mapping.select_next_item({ behavior = cmp.SelectBehavior.Insert }),
          ["<C-p>"]   = cmp.mapping.select_prev_item({ behavior = cmp.SelectBehavior.Insert }),

          -- Scroll documentation
          ["<C-b>"]   = cmp.mapping.scroll_docs(-4),
          ["<C-f>"]   = cmp.mapping.scroll_docs(4),

          -- Confirm selection
          ["<CR>"]    = cmp.mapping.confirm({ select = true }),
          ["<C-y>"]   = cmp.mapping.confirm({ select = false }),

          -- Manually trigger completion
          ["<C-Space>"] = cmp.mapping.complete(),

          -- Dismiss completion menu
          ["<C-e>"]   = cmp.mapping.abort(),

          -- Tab: smart snippet/completion navigation
          ["<Tab>"] = cmp.mapping(function(fallback)
            if cmp.visible() then
              cmp.select_next_item()
            elseif luasnip.expand_or_jumpable() then
              luasnip.expand_or_jump()
            elseif has_words_before() then
              cmp.complete()
            else
              fallback()
            end
          end, { "i", "s" }),

          ["<S-Tab>"] = cmp.mapping(function(fallback)
            if cmp.visible() then
              cmp.select_prev_item()
            elseif luasnip.jumpable(-1) then
              luasnip.jump(-1)
            else
              fallback()
            end
          end, { "i", "s" }),
        }),

        -- ── Sources (ordered by priority) ────────────────────────────────
        sources = cmp.config.sources({
          { name = "nvim_lsp",  priority = 1000 },
          { name = "luasnip",   priority = 750  },
          { name = "nvim_lua",  priority = 500  },
          { name = "path",      priority = 250  },
        }, {
          { name = "buffer",    priority = 100, keyword_length = 3 },
        }),

        -- ── Formatting (icons and source labels) ─────────────────────────
        formatting = {
          expandable_indicator = true,
          format = lspkind.cmp_format({
            mode   = "symbol_text",
            maxwidth = 50,
            ellipsis_char = "...",
            menu = {
              nvim_lsp = "[LSP]",
              luasnip  = "[Snip]",
              nvim_lua = "[Lua]",
              buffer   = "[Buf]",
              path     = "[Path]",
              git      = "[Git]",
            },
          }),
        },

        -- ── Sorting ──────────────────────────────────────────────────────
        sorting = {
          priority_weight = 2,
          comparators = {
            cmp.config.compare.offset,
            cmp.config.compare.exact,
            cmp.config.compare.score,
            cmp.config.compare.recently_used,
            cmp.config.compare.locality,
            cmp.config.compare.kind,
            cmp.config.compare.length,
            cmp.config.compare.order,
          },
        },

        -- ── Experimental ─────────────────────────────────────────────────
        experimental = {
          ghost_text = { hl_group = "CmpGhostText" },
        },
      })

      -- ── Command-line completion ───────────────────────────────────────
      -- Search mode (/)
      cmp.setup.cmdline({ "/", "?" }, {
        mapping = cmp.mapping.preset.cmdline(),
        sources = {
          { name = "buffer" },
        },
      })

      -- Command mode (:)
      cmp.setup.cmdline(":", {
        mapping = cmp.mapping.preset.cmdline(),
        sources = cmp.config.sources({
          { name = "path" },
        }, {
          { name = "cmdline", option = { ignore_cmds = { "Man", "!" } } },
        }),
      })

      -- ── Git source setup ──────────────────────────────────────────────
      require("cmp_git").setup()
    end,
  },
}
```

---

## Custom Snippets

Create Lua snippets in `~/.config/nvim/snippets/<filetype>.lua`:

```lua
-- ~/.config/nvim/snippets/python.lua
local ls  = require("luasnip")
local s   = ls.snippet
local t   = ls.text_node
local i   = ls.insert_node
local fmt = require("luasnip.extras.fmt").fmt

return {
  -- Django view boilerplate
  s("djview", fmt([[
from django.shortcuts import render

def {}(request):
    context = {{}}
    return render(request, "{}.html", context)
]], { i(1, "view_name"), i(2, "template_name") })),

  -- pytest test function
  s("test", fmt([[
def test_{}():
    {}
    assert {}
]], { i(1, "function_name"), i(2, "# arrange"), i(3, "True") })),
}
```

---

## Key Reference

| Key           | Action                              |
|---------------|-------------------------------------|
| `<C-n>`       | Next completion item                |
| `<C-p>`       | Previous completion item            |
| `<CR>`        | Confirm selected item               |
| `<C-Space>`   | Manually trigger completion         |
| `<C-e>`       | Dismiss completion                  |
| `<Tab>`       | Next item / expand snippet          |
| `<S-Tab>`     | Previous item / jump back in snippet|
| `<C-b>`       | Scroll docs up                      |
| `<C-f>`       | Scroll docs down                    |

---

## Troubleshooting

### Completions not appearing

```vim
:lua require("cmp").setup()    -- verify cmp is loaded
:LspInfo                        -- verify LSP is attached
:checkhealth nvim-cmp
```

### Snippets not expanding

```lua
-- Check LuaSnip is loaded and snippets are registered
:lua require("luasnip").get_snippets()
```

### Ghost text not showing

Ensure your colorscheme defines `CmpGhostText`:

```lua
vim.api.nvim_set_hl(0, "CmpGhostText", { link = "Comment", default = true })
```

---

## Next Steps

1. [MERN Stack Setup](./06-mern-stack.md)
2. [Python Development](./07-python-setup.md)
