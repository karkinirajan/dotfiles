# Themes & UI Configuration

## Overview

A polished UI makes a huge difference in day-to-day editing. This guide covers:

| Component        | Plugin(s)                                     |
|-----------------|-----------------------------------------------|
| Color schemes    | Catppuccin, TokyoNight, Gruvbox, Kanagawa     |
| Status line      | lualine.nvim                                  |
| Buffer line      | bufferline.nvim                               |
| Dashboard        | dashboard-nvim / alpha-nvim                   |
| Indent guides    | indent-blankline.nvim                         |
| Icons            | nvim-web-devicons                             |
| Color preview    | nvim-colorizer.lua                            |
| Notifications    | nvim-notify / noice.nvim                      |
| Which-key        | which-key.nvim                                |

---

## Color Scheme

### Catppuccin (recommended)

```lua
-- lua/plugins/colorscheme.lua
return {
  {
    "catppuccin/nvim",
    name    = "catppuccin",
    priority = 1000,   -- load before other plugins
    opts = {
      flavour            = "mocha",    -- latte, frappe, macchiato, mocha
      background         = { light = "latte", dark = "mocha" },
      transparent_background = false,
      show_end_of_buffer = false,
      term_colors        = true,
      dim_inactive       = { enabled = false, shade = "dark", percentage = 0.15 },
      no_italic          = false,
      no_bold            = false,
      no_underline       = false,

      integrations = {
        cmp            = true,
        gitsigns       = true,
        neotree        = true,
        telescope      = { enabled = true },
        treesitter     = true,
        mason          = true,
        lsp_trouble    = true,
        which_key      = true,
        bufferline     = true,
        dashboard      = true,
        notify         = true,
        noice          = true,
        indent_blankline = { enabled = true, scope_color = "lavender" },
        native_lsp = {
          enabled        = true,
          virtual_text   = { errors = { "italic" }, hints = { "italic" }, warnings = { "italic" }, information = { "italic" } },
          underlines     = { errors = { "underline" }, hints = { "underline" }, warnings = { "underline" }, information = { "underline" } },
          inlay_hints    = { background = true },
        },
      },
    },
    config = function(_, opts)
      require("catppuccin").setup(opts)
      vim.cmd.colorscheme("catppuccin")
    end,
  },
}
```

### Other Popular Schemes

```lua
-- TokyoNight
{ "folke/tokyonight.nvim",       priority = 1000, opts = { style = "night" } },

-- Gruvbox Material
{ "sainnhe/gruvbox-material",    priority = 1000 },

-- Kanagawa
{ "rebelot/kanagawa.nvim",       priority = 1000, opts = { theme = "wave" } },

-- Rose Pine
{ "rose-pine/neovim",            name = "rose-pine", priority = 1000 },

-- Nightfox
{ "EdenEast/nightfox.nvim",      priority = 1000 },
```

---

## Lualine (Status Line)

```lua
-- lua/plugins/lualine.lua
return {
  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    event = "VeryLazy",
    opts = {
      options = {
        theme                  = "catppuccin",   -- or "auto" for any scheme
        component_separators   = { left = "", right = "" },
        section_separators     = { left = "", right = "" },
        globalstatus           = true,    -- single statusline across windows
        refresh = { statusline = 100 },  -- update every 100ms
      },

      sections = {
        lualine_a = {
          { "mode", separator = { left = "" }, right_padding = 2 },
        },
        lualine_b = {
          "branch",
          { "diff",       symbols = { added = " ", modified = " ", removed = " " } },
          { "diagnostics", symbols = { error = " ", warn = " ", info = " ", hint = "󰝶 " } },
        },
        lualine_c = {
          { "filename",   path = 1, symbols = { modified = "  ", readonly = " ", unnamed = " " } },
        },
        lualine_x = {
          { "filetype",  icon_only = true, separator = "", padding = { left = 1, right = 0 } },
          { "encoding" },
          { "fileformat", icons_enabled = true },
        },
        lualine_y = {
          { "progress", separator = " ", padding = { left = 1, right = 0 } },
          { "location", padding = { left = 0, right = 1 } },
        },
        lualine_z = {
          function() return " " .. os.date("%R") end,  -- clock
        },
      },

      -- Status line for inactive windows
      inactive_sections = {
        lualine_a = {},
        lualine_b = {},
        lualine_c = { "filename" },
        lualine_x = { "location" },
        lualine_y = {},
        lualine_z = {},
      },

      extensions = { "neo-tree", "lazy", "fugitive", "quickfix" },
    },
  },
}
```

---

## Bufferline (Tab Bar)

```lua
-- lua/plugins/bufferline.lua
return {
  {
    "akinsho/bufferline.nvim",
    version = "*",
    dependencies = "nvim-tree/nvim-web-devicons",
    event = "VeryLazy",
    keys = {
      { "<S-h>",        "<cmd>BufferLineCyclePrev<CR>",     desc = "Previous buffer" },
      { "<S-l>",        "<cmd>BufferLineCycleNext<CR>",     desc = "Next buffer" },
      { "<leader>bp",   "<cmd>BufferLineTogglePin<CR>",     desc = "Pin buffer" },
      { "<leader>bP",   "<cmd>BufferLineGroupClose ungrouped<CR>", desc = "Close unpinned buffers" },
      { "<leader>bd",   "<cmd>bdelete<CR>",                desc = "Close buffer" },
    },
    opts = {
      options = {
        mode             = "buffers",
        numbers          = "none",
        close_command    = "bdelete! %d",
        right_mouse_command = "bdelete! %d",
        indicator        = { icon = "▎", style = "icon" },
        buffer_close_icon = "󰅖",
        modified_icon    = "●",
        close_icon       = "",
        left_trunc_marker  = "",
        right_trunc_marker = "",
        diagnostics      = "nvim_lsp",
        diagnostics_update_in_insert = false,
        diagnostics_indicator = function(count, level)
          local icon = level:match("error") and " " or " "
          return " " .. icon .. count
        end,
        offsets = {
          {
            filetype   = "neo-tree",
            text       = "File Explorer",
            highlight  = "Directory",
            separator  = true,
          },
        },
        show_buffer_icons      = true,
        show_buffer_close_icons = true,
        show_close_icon        = true,
        show_tab_indicators    = true,
        separator_style        = "slant",   -- "slant" | "thick" | "thin"
        enforce_regular_tabs   = false,
        always_show_bufferline = false,
        hover = {
          enabled = true,
          delay   = 200,
          reveal  = { "close" },
        },
      },
    },
  },
}
```

---

## Dashboard / Start Screen

```lua
-- lua/plugins/dashboard.lua
return {
  {
    "nvimdev/dashboard-nvim",
    event = "VimEnter",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    opts = {
      theme = "hyper",
      config = {
        week_header = { enable = true },
        shortcut = {
          { desc = "󰊳 Update",  group = "@property", action = "Lazy update",           key = "u" },
          { desc = "  Files",   group = "Label",      action = "Telescope find_files",  key = "f" },
          { desc = "  Grep",    group = "Label",      action = "Telescope live_grep",   key = "g" },
          { desc = "  Recent",  group = "Number",     action = "Telescope oldfiles",    key = "r" },
          { desc = "  Config",  group = "Number",     action = "edit ~/.config/nvim/init.lua", key = "c" },
          { desc = "  Quit",    group = "Number",     action = "quit",                  key = "q" },
        },
        project = { enable = true, limit = 8 },
        mru     = { limit = 10, icon = " ", label = "Recent Files" },
        footer  = { "", "🎉 Neovim loaded" },
      },
    },
  },
}
```

---

## Indent Guides

```lua
-- lua/plugins/indent.lua
return {
  {
    "lukas-reineke/indent-blankline.nvim",
    main  = "ibl",
    event = { "BufReadPre", "BufNewFile" },
    opts  = {
      indent = {
        char       = "│",
        tab_char   = "│",
      },
      scope = {
        enabled    = true,
        show_start = true,
        show_end   = false,
      },
      exclude = {
        filetypes = {
          "help", "dashboard", "neo-tree", "Trouble",
          "lazy", "mason", "notify", "toggleterm",
        },
      },
    },
  },
}
```

---

## Notifications & Command UI (Noice)

```lua
-- lua/plugins/noice.lua
return {
  {
    "folke/noice.nvim",
    event = "VeryLazy",
    dependencies = { "MunifTanjim/nui.nvim", "rcarriga/nvim-notify" },
    opts = {
      lsp = {
        override = {
          ["vim.lsp.util.convert_input_to_markdown_lines"] = true,
          ["vim.lsp.util.stylize_markdown"]                = true,
          ["cmp.entry.get_documentation"]                  = true,
        },
      },
      routes = {
        { filter = { event = "msg_show", kind = "", find = "written" }, opts = { skip = true } },
        { filter = { event = "msg_show", kind = "", find = "fewer lines" }, opts = { skip = true } },
      },
      presets = {
        bottom_search         = true,
        command_palette       = true,
        long_message_to_split = true,
        inc_rename            = false,
      },
    },
    keys = {
      { "<leader>sn",  function() require("noice").cmd("dismiss") end, desc = "Dismiss notifications" },
      { "<leader>nl",  function() require("noice").cmd("last") end,    desc = "Last notification" },
      { "<leader>nh",  function() require("noice").cmd("history") end, desc = "Notification history" },
    },
  },
}
```

---

## Color Previews

```lua
{
  "NvChad/nvim-colorizer.lua",
  event = { "BufReadPre", "BufNewFile" },
  opts = {
    user_default_options = {
      RGB      = true,
      RRGGBB   = true,
      names    = true,
      css      = true,
      css_fn   = true,
      tailwind = "both",    -- also show Tailwind class colors
      mode     = "background",  -- "foreground" | "background" | "virtualtext"
    },
  },
}
```

---

## Which-Key (Keymap Discovery)

```lua
{
  "folke/which-key.nvim",
  event = "VeryLazy",
  opts = {
    preset   = "modern",
    delay    = 400,
    icons    = { mappings = true },
    plugins  = { spelling = { enabled = true } },
    spec = {
      { "<leader>f",  group = "find/files" },
      { "<leader>g",  group = "git" },
      { "<leader>h",  group = "git hunks" },
      { "<leader>t",  group = "tests" },
      { "<leader>d",  group = "debug/diff" },
      { "<leader>b",  group = "buffers" },
      { "<leader>c",  group = "code actions" },
    },
  },
}
```

---

## Core UI Options

Add to `lua/config/options.lua`:

```lua
-- Appearance
vim.opt.termguicolors  = true    -- 24-bit colour
vim.opt.cursorline     = true    -- highlight current line
vim.opt.number         = true    -- line numbers
vim.opt.relativenumber = true    -- relative line numbers
vim.opt.signcolumn     = "yes"   -- always show sign column
vim.opt.showmode       = false   -- mode shown by lualine
vim.opt.cmdheight      = 0       -- hide command line when not in use (Neovim 0.8+)
vim.opt.pumheight      = 10      -- max completion popup height
vim.opt.pumblend       = 10      -- slight transparency for popup
vim.opt.winblend       = 10      -- slight transparency for floating windows

-- Split behaviour
vim.opt.splitright     = true
vim.opt.splitbelow     = true

-- Scroll
vim.opt.scrolloff      = 8       -- lines to keep above/below cursor
vim.opt.sidescrolloff  = 8
```

---

## Troubleshooting

### Colors not showing correctly

```lua
-- Ensure terminal supports 24-bit colour; add to options:
vim.opt.termguicolors = true
```

### Icons showing as boxes/question marks

```bash
# Install and configure a Nerd Font in your terminal
# e.g. JetBrainsMono Nerd Font, FiraCode Nerd Font
# After installing, set it as your terminal font
```

### Noice breaking command-line experience

```lua
-- Disable noice for the command line specifically:
views = {
  cmdline_popup = { position = { row = "40%", col = "50%" } },
},
presets = { command_palette = false },
```

---

## Next Steps

1. [Performance Optimization](./20-performance.md)
