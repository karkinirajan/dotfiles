# File Explorer & Navigation

## Overview

Efficient navigation is one of the biggest productivity multipliers in Neovim.
This guide covers:

| Plugin              | Purpose                                        |
|---------------------|------------------------------------------------|
| **Telescope**       | Fuzzy finder — files, text, LSP symbols, etc.  |
| **Neo-tree**        | Sidebar file explorer                          |
| **Harpoon**         | Quick-jump between marked files                |
| **Flash / Leap**    | Instant cursor motion anywhere on screen       |
| **Oil.nvim**        | Edit the filesystem like a buffer              |

---

## Telescope

```lua
-- lua/plugins/telescope.lua
return {
  {
    "nvim-telescope/telescope.nvim",
    branch = "0.1.x",
    dependencies = {
      "nvim-lua/plenary.nvim",
      { "nvim-telescope/telescope-fzf-native.nvim", build = "make" },
      "nvim-telescope/telescope-ui-select.nvim",
      "nvim-telescope/telescope-file-browser.nvim",
      "nvim-tree/nvim-web-devicons",
    },
    keys = {
      -- Files
      { "<leader>ff",  "<cmd>Telescope find_files<CR>",                       desc = "Find files" },
      { "<leader>fF",  "<cmd>Telescope find_files hidden=true<CR>",           desc = "Find files (incl. hidden)" },
      { "<leader>fr",  "<cmd>Telescope oldfiles<CR>",                         desc = "Recent files" },
      { "<leader>fb",  "<cmd>Telescope buffers sort_mru=true<CR>",            desc = "Buffers" },
      { "<leader>fg",  "<cmd>Telescope live_grep<CR>",                        desc = "Live grep" },
      { "<leader>fG",  "<cmd>Telescope grep_string<CR>",                      desc = "Grep word under cursor" },
      { "<leader>fw",  "<cmd>Telescope grep_string<CR>",                      desc = "Find word" },
      -- Git
      { "<leader>gc",  "<cmd>Telescope git_commits<CR>",                      desc = "Git commits" },
      { "<leader>gb",  "<cmd>Telescope git_branches<CR>",                     desc = "Git branches" },
      { "<leader>gs",  "<cmd>Telescope git_status<CR>",                       desc = "Git status" },
      -- LSP
      { "<leader>fd",  "<cmd>Telescope diagnostics<CR>",                      desc = "Diagnostics" },
      { "<leader>fs",  "<cmd>Telescope lsp_document_symbols<CR>",             desc = "Document symbols" },
      { "<leader>fS",  "<cmd>Telescope lsp_workspace_symbols<CR>",            desc = "Workspace symbols" },
      { "<leader>fi",  "<cmd>Telescope lsp_implementations<CR>",              desc = "Implementations" },
      -- Misc
      { "<leader>fh",  "<cmd>Telescope help_tags<CR>",                        desc = "Help tags" },
      { "<leader>fk",  "<cmd>Telescope keymaps<CR>",                          desc = "Keymaps" },
      { "<leader>fc",  "<cmd>Telescope commands<CR>",                         desc = "Commands" },
      { "<leader>f:",  "<cmd>Telescope command_history<CR>",                  desc = "Command history" },
      { "<leader>fe",  "<cmd>Telescope file_browser path=%:p:h<CR>",          desc = "File browser" },
    },
    config = function()
      local telescope = require("telescope")
      local actions   = require("telescope.actions")

      telescope.setup({
        defaults = {
          prompt_prefix   = "  ",
          selection_caret = "  ",
          entry_prefix    = "  ",
          multi_icon      = " ",
          sorting_strategy = "ascending",
          layout_config = {
            horizontal = { prompt_position = "top", preview_width = 0.55 },
            vertical   = { mirror = false },
            width      = 0.87,
            height     = 0.80,
            preview_cutoff = 120,
          },
          mappings = {
            i = {
              ["<C-j>"]   = actions.move_selection_next,
              ["<C-k>"]   = actions.move_selection_previous,
              ["<C-q>"]   = actions.send_selected_to_qflist + actions.open_qflist,
              ["<C-a>"]   = actions.select_all,
              ["<Esc>"]   = actions.close,
              ["<C-u>"]   = false,  -- clear input (default Telescope override)
            },
            n = {
              ["q"]       = actions.close,
            },
          },
          file_ignore_patterns = {
            "node_modules", ".git/", "dist/", "build/",
            ".next/", "__pycache__", "*.pyc",
          },
        },

        extensions = {
          fzf = {
            fuzzy                   = true,
            override_generic_sorter = true,
            override_file_sorter    = true,
            case_mode               = "smart_case",
          },
          ["ui-select"] = {
            require("telescope.themes").get_dropdown(),
          },
        },
      })

      telescope.load_extension("fzf")
      telescope.load_extension("ui-select")
      telescope.load_extension("file_browser")
    end,
  },
}
```

---

## Neo-tree (File Explorer)

```lua
-- lua/plugins/neo-tree.lua
return {
  {
    "nvim-neo-tree/neo-tree.nvim",
    branch = "v3.x",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "nvim-tree/nvim-web-devicons",
      "MunifTanjim/nui.nvim",
      "3rd/image.nvim",  -- optional: image preview
    },
    keys = {
      { "<leader>e",  "<cmd>Neotree toggle<CR>",          desc = "Toggle file explorer" },
      { "<leader>E",  "<cmd>Neotree reveal<CR>",          desc = "Reveal current file" },
      { "<leader>ge", "<cmd>Neotree git_status<CR>",      desc = "Git status (neo-tree)" },
    },
    opts = {
      close_if_last_window = true,
      window = {
        position = "left",
        width    = 35,
        mappings = {
          ["<space>"] = "none",
          ["l"]       = "open",
          ["h"]       = "close_node",
          ["H"]       = "toggle_hidden",
          ["<C-x>"]   = "open_split",
          ["<C-v>"]   = "open_vsplit",
          ["<C-t>"]   = "open_tabnew",
          ["a"]       = "add",
          ["d"]       = "delete",
          ["r"]       = "rename",
          ["c"]       = "copy",
          ["m"]       = "move",
          ["y"]       = "copy_to_clipboard",
          ["x"]       = "cut_to_clipboard",
          ["p"]       = "paste_from_clipboard",
          ["q"]       = "close_window",
          ["R"]       = "refresh",
          ["?"]       = "show_help",
        },
      },
      filesystem = {
        filtered_items = {
          hide_dotfiles     = false,
          hide_gitignored   = true,
          hide_by_name      = { ".git", "node_modules", "__pycache__" },
        },
        follow_current_file = {
          enabled           = true,
          leave_dirs_open   = false,
        },
        use_libuv_file_watcher = true,
      },
      git_status = {
        window = { position = "float" },
      },
    },
  },
}
```

---

## Harpoon 2 (Quick File Marks)

```lua
-- lua/plugins/harpoon.lua
return {
  {
    "ThePrimeagen/harpoon",
    branch = "harpoon2",
    dependencies = { "nvim-lua/plenary.nvim" },
    keys = function()
      local harpoon = require("harpoon")
      local keys = {
        { "<leader>ha", function() harpoon:list():add() end,       desc = "Harpoon: add file" },
        { "<leader>hh", function() harpoon.ui:toggle_quick_menu(harpoon:list()) end, desc = "Harpoon: menu" },
      }
      -- Slots 1–5 via Ctrl+1 through Ctrl+5
      for i = 1, 5 do
        table.insert(keys, {
          "<C-" .. i .. ">",
          function() harpoon:list():select(i) end,
          desc = "Harpoon: file " .. i,
        })
      end
      return keys
    end,
    config = function()
      require("harpoon"):setup({
        settings = {
          save_on_toggle = true,
          sync_on_ui_close = false,
        },
      })
    end,
  },
}
```

---

## Flash.nvim (Screen Motions)

Flash replaces and extends `s`/`S` motions with instant label-based navigation:

```lua
-- lua/plugins/flash.lua
return {
  {
    "folke/flash.nvim",
    event = "VeryLazy",
    keys = {
      { "s",      mode = { "n", "x", "o" }, function() require("flash").jump() end,             desc = "Flash jump" },
      { "S",      mode = { "n", "x", "o" }, function() require("flash").treesitter() end,       desc = "Flash treesitter node" },
      { "r",      mode = "o",               function() require("flash").remote() end,            desc = "Flash remote" },
      { "R",      mode = { "o", "x" },      function() require("flash").treesitter_search() end, desc = "Flash treesitter search" },
      { "<C-s>",  mode = { "c" },           function() require("flash").toggle() end,            desc = "Flash: toggle in search" },
    },
    opts = {
      modes = {
        char  = { enabled = false },  -- keep default f/t/F/T behaviour
        search = { enabled = true },  -- enhance / search with labels
      },
    },
  },
}
```

---

## Oil.nvim (Filesystem as Buffer)

```lua
-- lua/plugins/oil.lua
return {
  {
    "stevearc/oil.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    keys = {
      { "-", "<cmd>Oil<CR>", desc = "Open parent directory (oil)" },
    },
    opts = {
      default_file_explorer  = false,  -- keep neo-tree as default
      delete_to_trash        = true,
      skip_confirm_for_simple_edits = true,
      view_options = {
        show_hidden = true,
        is_hidden_file = function(name, bufnr)
          return vim.startswith(name, ".")
        end,
      },
      keymaps = {
        ["g?"]   = "actions.show_help",
        ["<CR>"] = "actions.select",
        ["-"]    = "actions.parent",
        ["_"]    = "actions.open_cwd",
        ["`"]    = "actions.cd",
        ["~"]    = "actions.tcd",
        ["gs"]   = "actions.change_sort",
        ["gx"]   = "actions.open_external",
        ["g."]   = "actions.toggle_hidden",
        ["q"]    = "actions.close",
      },
    },
  },
}
```

---

## Key Mappings Summary

### Telescope

| Keymap        | Action                          |
|---------------|---------------------------------|
| `<leader>ff`  | Find files                      |
| `<leader>fg`  | Live grep                       |
| `<leader>fb`  | Buffers                         |
| `<leader>fr`  | Recent files                    |
| `<leader>fs`  | Document symbols (LSP)          |
| `<leader>fS`  | Workspace symbols (LSP)         |
| `<leader>fd`  | Diagnostics                     |
| `<leader>gc`  | Git commits                     |
| `<leader>fe`  | File browser                    |

### Navigation

| Keymap        | Action                                  |
|---------------|-----------------------------------------|
| `<leader>e`   | Toggle file explorer (Neo-tree)         |
| `<leader>E`   | Reveal current file in tree             |
| `<leader>ha`  | Add file to Harpoon                     |
| `<leader>hh`  | Open Harpoon menu                       |
| `<C-1>`–`<C-5>` | Jump to Harpoon slots 1–5            |
| `s`           | Flash jump (label-based motion)         |
| `S`           | Flash Treesitter node select            |
| `-`           | Open parent directory with Oil          |

---

## Troubleshooting

### Telescope fzf native not working

```bash
# Rebuild the native extension
cd ~/.local/share/nvim/lazy/telescope-fzf-native.nvim && make
```

### Neo-tree icons not showing

```bash
# Install a Nerd Font (e.g. JetBrainsMono Nerd Font)
# Then set it in your terminal emulator
```

### Flash labels not visible

```lua
-- Ensure your colorscheme defines FlashLabel
vim.api.nvim_set_hl(0, "FlashLabel", { bg = "#ff007c", fg = "#ffffff", bold = true })
```

---

## Next Steps

1. [Themes & UI](./19-themes-ui.md)
2. [Performance Optimization](./20-performance.md)
