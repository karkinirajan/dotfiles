# Git & GitHub Integration

## Overview

Neovim has a rich Git ecosystem. This guide covers:

| Plugin          | Purpose                                    |
|-----------------|--------------------------------------------|
| `vim-fugitive`  | Full Git client inside Neovim              |
| `gitsigns.nvim` | In-buffer diff signs, blame, hunk actions  |
| `lazygit.nvim`  | Terminal UI for Git inside Neovim          |
| `neogit`        | Magit-inspired Git interface               |
| `diffview.nvim` | Side-by-side diff viewer and merge tool    |

---

## Plugin Setup

```lua
-- lua/plugins/git.lua
return {
  -- ── Fugitive ─────────────────────────────────────────────────────────
  {
    "tpope/vim-fugitive",
    cmd = { "Git", "G", "Gread", "Gwrite", "Gdiffsplit", "GBrowse" },
    keys = {
      { "<leader>gs",  "<cmd>Git<CR>",                    desc = "Git status (fugitive)" },
      { "<leader>gb",  "<cmd>Git blame<CR>",              desc = "Git blame" },
      { "<leader>gd",  "<cmd>Gdiffsplit<CR>",             desc = "Git diff split" },
      { "<leader>gl",  "<cmd>Git log --oneline<CR>",      desc = "Git log" },
      { "<leader>gp",  "<cmd>Git push<CR>",               desc = "Git push" },
      { "<leader>gP",  "<cmd>Git pull<CR>",               desc = "Git pull" },
      { "<leader>gc",  "<cmd>Git commit<CR>",             desc = "Git commit" },
      { "<leader>ga",  "<cmd>Git add %<CR>",              desc = "Git add current file" },
    },
  },

  -- ── Gitsigns ─────────────────────────────────────────────────────────
  {
    "lewis6991/gitsigns.nvim",
    event = { "BufReadPre", "BufNewFile" },
    opts = {
      signs = {
        add          = { text = "▎" },
        change       = { text = "▎" },
        delete       = { text = "" },
        topdelete    = { text = "" },
        changedelete = { text = "▎" },
        untracked    = { text = "▎" },
      },

      -- Show blame info at the end of the line
      current_line_blame = true,
      current_line_blame_opts = {
        delay        = 300,
        virt_text_pos = "eol",
      },

      on_attach = function(bufnr)
        local gs = package.loaded.gitsigns

        local function map(mode, l, r, opts)
          opts        = opts or {}
          opts.buffer = bufnr
          vim.keymap.set(mode, l, r, opts)
        end

        -- Navigation
        map("n", "]h", function()
          if vim.wo.diff then return "]c" end
          vim.schedule(function() gs.next_hunk() end)
          return "<Ignore>"
        end, { expr = true, desc = "Next git hunk" })

        map("n", "[h", function()
          if vim.wo.diff then return "[c" end
          vim.schedule(function() gs.prev_hunk() end)
          return "<Ignore>"
        end, { expr = true, desc = "Previous git hunk" })

        -- Actions
        map("n", "<leader>hs", gs.stage_hunk,          { desc = "Stage hunk" })
        map("n", "<leader>hr", gs.reset_hunk,          { desc = "Reset hunk" })
        map("n", "<leader>hS", gs.stage_buffer,        { desc = "Stage buffer" })
        map("n", "<leader>hu", gs.undo_stage_hunk,     { desc = "Undo stage hunk" })
        map("n", "<leader>hR", gs.reset_buffer,        { desc = "Reset buffer" })
        map("n", "<leader>hp", gs.preview_hunk,        { desc = "Preview hunk" })
        map("n", "<leader>hb", function() gs.blame_line({ full = true }) end, { desc = "Blame line (full)" })
        map("n", "<leader>hd", gs.diffthis,            { desc = "Diff this" })
        map("n", "<leader>hD", function() gs.diffthis("~") end, { desc = "Diff this ~" })
        map("n", "<leader>td", gs.toggle_deleted,      { desc = "Toggle deleted lines" })

        -- Text objects
        map({ "o", "x" }, "ih", ":<C-U>Gitsigns select_hunk<CR>", { desc = "Select hunk" })
      end,
    },
  },

  -- ── Lazygit ──────────────────────────────────────────────────────────
  {
    "kdheepak/lazygit.nvim",
    cmd = { "LazyGit", "LazyGitConfig", "LazyGitCurrentFile", "LazyGitFilter", "LazyGitFilterCurrentFile" },
    dependencies = { "nvim-lua/plenary.nvim" },
    keys = {
      { "<leader>gg", "<cmd>LazyGit<CR>",              desc = "LazyGit" },
      { "<leader>gf", "<cmd>LazyGitCurrentFile<CR>",   desc = "LazyGit (current file log)" },
    },
  },

  -- ── Diffview ─────────────────────────────────────────────────────────
  {
    "sindrets/diffview.nvim",
    cmd = { "DiffviewOpen", "DiffviewClose", "DiffviewFileHistory", "DiffviewFocusFiles" },
    keys = {
      { "<leader>dv",  "<cmd>DiffviewOpen<CR>",            desc = "Open diff view" },
      { "<leader>dV",  "<cmd>DiffviewClose<CR>",           desc = "Close diff view" },
      { "<leader>dh",  "<cmd>DiffviewFileHistory %<CR>",   desc = "File history" },
      { "<leader>dH",  "<cmd>DiffviewFileHistory<CR>",     desc = "Repo history" },
    },
    opts = {
      enhanced_diff_hl = true,
      use_icons = true,
    },
  },
}
```

---

## Fugitive Workflow

### Status screen (`:Git`)

Inside the fugitive status buffer:

| Key     | Action                          |
|---------|---------------------------------|
| `s`     | Stage file / hunk               |
| `u`     | Unstage file / hunk             |
| `=`     | Toggle inline diff              |
| `cc`    | Commit                          |
| `ca`    | Amend last commit               |
| `cw`    | Reword last commit message      |
| `cf`    | Fixup last commit               |
| `dv`    | Diff split for file             |
| `dd`    | Diff split in new tab           |
| `o`     | Open file                       |
| `gO`    | Open file in vertical split     |
| `P`     | Push                            |
| `p`     | Pull                            |
| `q`     | Close                           |
| `g?`    | Show all available keymaps      |

### Blame buffer (`:Git blame`)

| Key     | Action                          |
|---------|---------------------------------|
| `<CR>`  | Jump to commit                  |
| `o`     | Open commit in split            |
| `A`     | Resize to author column         |
| `D`     | Resize to date column           |
| `q`     | Close blame                     |

### Three-way merge conflict resolution

```vim
:Gdiffsplit!   " Open 3-way merge: LOCAL | WORKING | REMOTE
```

| Key            | Action                          |
|----------------|---------------------------------|
| `d2o` / `:diffget //2` | Accept LOCAL (left)   |
| `d3o` / `:diffget //3` | Accept REMOTE (right) |
| `]c` / `[c`    | Navigate conflict hunks         |
| `:diffupdate`  | Refresh diff highlights         |

---

## Gitsigns Quick Reference

| Keymap       | Action                              |
|--------------|-------------------------------------|
| `]h`         | Next hunk                           |
| `[h`         | Previous hunk                       |
| `<leader>hs` | Stage hunk                          |
| `<leader>hr` | Reset hunk                          |
| `<leader>hS` | Stage entire buffer                 |
| `<leader>hu` | Undo last staged hunk               |
| `<leader>hp` | Preview hunk (inline diff popup)    |
| `<leader>hb` | Full blame for current line         |
| `<leader>td` | Toggle showing deleted lines        |
| `ih`         | Text object: inner hunk (o/x mode)  |

---

## Advanced: Git Worktrees

Git worktrees let you check out multiple branches simultaneously:

```bash
# Create a new worktree
git worktree add ../my-feature feature/my-feature

# List worktrees
git worktree list

# Remove a worktree
git worktree remove ../my-feature
```

### Telescope Worktree Picker (optional)

```lua
{
  "ThePrimeagen/git-worktree.nvim",
  config = function()
    require("telescope").load_extension("git_worktree")
  end,
  keys = {
    { "<leader>gw",  function() require("telescope").extensions.git_worktree.git_worktrees() end,        desc = "Switch worktree" },
    { "<leader>gW",  function() require("telescope").extensions.git_worktree.create_git_worktree() end,  desc = "Create worktree" },
  },
}
```

---

## GitHub Integration

### Open current file on GitHub

```vim
" With vim-fugitive + vim-rhubarb installed:
:GBrowse    " Opens current file/selection on GitHub
```

```lua
-- Add to plugins:
{ "tpope/vim-rhubarb" }  -- GitHub extension for fugitive
```

### PR review in Neovim (optional)

```lua
{
  "pwntester/octo.nvim",
  dependencies = {
    "nvim-lua/plenary.nvim",
    "nvim-telescope/telescope.nvim",
    "nvim-tree/nvim-web-devicons",
  },
  cmd = "Octo",
  config = true,
}
```

Usage:

```vim
:Octo pr list          " List open PRs
:Octo pr checkout 42   " Checkout PR #42
:Octo review start     " Start a review
:Octo comment add      " Add a comment
```

---

## Troubleshooting

### Gitsigns not showing

```vim
:checkhealth gitsigns
" Ensure the buffer is in a git repo
:lua print(vim.fn.system("git rev-parse --show-toplevel"))
```

### LazyGit not found

```bash
# Arch
sudo pacman -S lazygit

# macOS
brew install lazygit

# Or download binary from GitHub releases
```

### Fugitive slow on large repos

Add sparse checkout or reduce log depth:

```vim
:Git log --max-count=200
```

---

## Next Steps

1. [CI/CD Tools](./15-cicd-tools.md)
2. [Debugging](./16-debugging.md)
