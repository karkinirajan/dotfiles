# Python Development (Django/FastAPI/Flask)

## LSP Servers

Install via Mason:

```vim
:MasonInstall pyright ruff_lsp debugpy
```

Or configure in `lua/plugins/lsp.lua`:

```lua
ensure_installed = {
  "pyright",       -- Type checking & IntelliSense
  "ruff_lsp",      -- Fast linting & formatting
  "debugpy",       -- Python debugger
}
```

## Virtual Environment Management

```lua
-- lua/plugins/python.lua
return {
  -- Auto-detect and activate virtual environments
  {
    "linux-cultist/venv-selector.nvim",
    dependencies = {
      "neovim/nvim-lspconfig",
      "nvim-telescope/telescope.nvim",
      "mfussenegger/nvim-dap-python",
    },
    opts = {
      name = { "venv", ".venv", "env", ".env" },
      auto_refresh = true,
    },
    keys = {
      { "<leader>vs", "<cmd>VenvSelect<cr>", desc = "Select VirtualEnv" },
      { "<leader>vc", "<cmd>VenvSelectCached<cr>", desc = "Select Cached VirtualEnv" },
    },
  },
}
```

## Django-Specific Setup

### Django LSP

```bash
# Install Django Language Server
pip install django-types django-stubs djangorestframework-stubs
```

### Configuration

```lua
-- lua/plugins/django.lua
return {
  -- Django template syntax
  {
    "tweekmonster/django-plus.vim",
    ft = { "python", "htmldjango" },
  },

  -- Django commands
  {
    "nvim-neotest/neotest",
    dependencies = { "nvim-neotest/neotest-python" },
    config = function()
      require("neotest").setup({
        adapters = {
          require("neotest-python")({
            runner = "pytest",
            dap = { justMyCode = false },
            args = { "--log-level", "DEBUG" },
          }),
        },
      })
    end,
  },
}
```

### Django Keymaps

```lua
-- For Django projects
vim.api.nvim_create_autocmd("FileType", {
  pattern = "python",
  callback = function()
    if vim.fn.filereadable("manage.py") == 1 then
      vim.keymap.set("n", "<leader>dm", ":!python manage.py<Space>", { desc = "Django manage.py" })
      vim.keymap.set("n", "<leader>dr", ":!python manage.py runserver<CR>", { desc = "Django runserver" })
      vim.keymap.set("n", "<leader>dt", ":!python manage.py test<CR>", { desc = "Django test" })
      vim.keymap.set("n", "<leader>ds", ":!python manage.py shell<CR>", { desc = "Django shell" })
      vim.keymap.set("n", "<leader>dd", ":!python manage.py makemigrations<CR>", { desc = "Django makemigrations" })
      vim.keymap.set("n", "<leader>dg", ":!python manage.py migrate<CR>", { desc = "Django migrate" })
    end
  end,
})
```

## FastAPI Setup

### Auto-completion for FastAPI

```lua
-- Pyright settings for FastAPI
lspconfig.pyright.setup({
  capabilities = capabilities,
  settings = {
    python = {
      analysis = {
        typeCheckingMode = "basic",
        autoImportCompletions = true,
        diagnosticMode = "workspace",
      }
    }
  },
  on_attach = function(client, bufnr)
    -- FastAPI-specific keymaps
    if vim.fn.filereadable("main.py") == 1 then
      vim.keymap.set("n", "<leader>fr", ":!uvicorn main:app --reload<CR>", { buffer = bufnr })
    end
  end,
})
```

### FastAPI Snippets

```lua
local ls = require("luasnip")
ls.add_snippets("python", {
  ls.snippet("fastapi_get", {
    ls.text_node({"@app.get('/')", "async def read_root():", "    return {'Hello': 'World'}"}),
  }),
  ls.snippet("fastapi_post", {
    ls.text_node({"@app.post('/items/')", "async def create_item(item: Item):", "    return item"}),
  }),
})
```

## Flask Setup

### Flask Keymaps

```lua
vim.api.nvim_create_autocmd("FileType", {
  pattern = "python",
  callback = function()
    if vim.fn.filereadable("app.py") == 1 or vim.fn.filereadable("wsgi.py") == 1 then
      vim.keymap.set("n", "<leader>fr", ":!flask run<CR>", { desc = "Flask run" })
      vim.keymap.set("n", "<leader>fs", ":!flask shell<CR>", { desc = "Flask shell" })
    end
  end,
})
```

## Python Formatting & Linting

### Install Tools

```vim
:MasonInstall ruff black mypy
```

### Configure

```lua
-- lua/plugins/formatting.lua
formatters_by_ft = {
  python = { "ruff_format", "black" },
}

-- lua/plugins/linting.lua
linters_by_ft = {
  python = { "ruff", "mypy" },
}
```

## Python Debugging

```lua
-- lua/plugins/dap-python.lua
return {
  {
    "mfussenegger/nvim-dap-python",
    ft = "python",
    dependencies = {
      "mfussenegger/nvim-dap",
      "rcarriga/nvim-dap-ui",
    },
    config = function()
      -- Path to debugpy
      local debugpy_path = vim.fn.stdpath("data") .. "/mason/packages/debugpy/venv/bin/python"
      require("dap-python").setup(debugpy_path)

      -- Django configurations
      table.insert(require("dap").configurations.python, {
        type = "python",
        request = "launch",
        name = "Django",
        program = vim.fn.getcwd() .. "/manage.py",
        args = { "runserver", "--noreload" },
        django = true,
        justMyCode = false,
      })

      -- FastAPI configuration
      table.insert(require("dap").configurations.python, {
        type = "python",
        request = "launch",
        name = "FastAPI",
        module = "uvicorn",
        args = { "main:app", "--reload" },
        jinja = true,
        justMyCode = false,
      })
    end,
  },
}
```

## Testing

```lua
-- lua/plugins/testing.lua
return {
  {
    "nvim-neotest/neotest",
    dependencies = {
      "nvim-neotest/neotest-python",
    },
    keys = {
      { "<leader>tt", "<cmd>lua require('neotest').run.run()<cr>" },
      { "<leader>tf", "<cmd>lua require('neotest').run.run(vim.fn.expand('%'))<cr>" },
      { "<leader>td", "<cmd>lua require('neotest').run.run({strategy = 'dap'})<cr>" },
    },
    config = function()
      require("neotest").setup({
        adapters = {
          require("neotest-python")({
            dap = { justMyCode = false },
            runner = "pytest",
            python = ".venv/bin/python",
          }),
        },
      })
    end,
  },
}
```

## Project Setup

### Django Project

```bash
# Create project
python -m venv .venv
source .venv/bin/activate
pip install django djangorestframework django-types
django-admin startproject myproject .

# In Neovim
nvim manage.py
:VenvSelect  # Select .venv
```

### FastAPI Project

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn[standard] python-multipart

# Create main.py
nvim main.py
```

### Requirements Management

```vim
:!pip freeze > requirements.txt
:!pip install -r requirements.txt
```

## Recommended Settings

```lua
-- Python-specific settings
vim.api.nvim_create_autocmd("FileType", {
  pattern = "python",
  callback = function()
    vim.opt_local.tabstop = 4
    vim.opt_local.shiftwidth = 4
    vim.opt_local.expandtab = true
    vim.opt_local.colorcolumn = "88"  -- Black's line length
  end,
})
```

## Next Steps

- [SQL Databases](./09-sql-databases.md)
- [Debugging](./16-debugging.md)
- [Testing](./17-testing.md)
