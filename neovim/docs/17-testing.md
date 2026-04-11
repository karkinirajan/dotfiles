# Testing Integration

## Overview

**Neotest** is the standard Neovim test runner framework. It has adapters for most
popular test frameworks and provides:

- Run individual tests, files, or entire suites
- Inline test result indicators in the sign column
- Output panel with test output
- Quickfix integration for failures
- Watch mode (re-run on file change)

---

## Plugin Setup

```lua
-- lua/plugins/testing.lua
return {
  {
    "nvim-neotest/neotest",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "antoinemadec/FixCursorHold.nvim",
      "nvim-treesitter/nvim-treesitter",

      -- Adapters
      "nvim-neotest/neotest-python",        -- pytest, unittest
      "nvim-neotest/neotest-jest",          -- Jest (JS/TS)
      "marilari88/neotest-vitest",          -- Vitest
      "nvim-neotest/neotest-go",            -- Go (testing package)
      "rouge8/neotest-rust",                -- Rust (cargo test)
    },
    keys = {
      { "<leader>tt",  function() require("neotest").run.run() end,                                          desc = "Run nearest test" },
      { "<leader>tf",  function() require("neotest").run.run(vim.fn.expand("%")) end,                        desc = "Run test file" },
      { "<leader>tl",  function() require("neotest").run.run_last() end,                                     desc = "Re-run last test" },
      { "<leader>ts",  function() require("neotest").run.run({ suite = true }) end,                          desc = "Run test suite" },
      { "<leader>to",  function() require("neotest").output.open({ enter = true }) end,                      desc = "Open test output" },
      { "<leader>tO",  function() require("neotest").output_panel.toggle() end,                              desc = "Toggle output panel" },
      { "<leader>tS",  function() require("neotest").summary.toggle() end,                                   desc = "Toggle summary panel" },
      { "<leader>tw",  function() require("neotest").watch.toggle(vim.fn.expand("%")) end,                   desc = "Watch test file" },
      { "<leader>td",  function() require("neotest").run.run({ strategy = "dap" }) end,                      desc = "Debug nearest test" },
      { "]t",          function() require("neotest").jump.next({ status = "failed" }) end,                   desc = "Next failed test" },
      { "[t",          function() require("neotest").jump.prev({ status = "failed" }) end,                   desc = "Previous failed test" },
    },
    config = function()
      local neotest = require("neotest")

      neotest.setup({
        adapters = {
          -- ── Python ───────────────────────────────────────────────────
          require("neotest-python")({
            dap = { justMyCode = false },
            args = { "--log-level", "DEBUG", "-v" },
            runner = "pytest",               -- or "unittest"
            python = function()
              -- Use virtual environment's Python if available
              local venv = vim.fn.findfile("pyproject.toml", vim.fn.getcwd() .. ";")
              if venv ~= "" then
                return ".venv/bin/python"
              end
              return "python3"
            end,
          }),

          -- ── Jest ─────────────────────────────────────────────────────
          require("neotest-jest")({
            jestCommand = "npx jest",
            jestConfigFile = function(file)
              -- Find the nearest jest.config.*
              local path = vim.fn.fnamemodify(file, ":p")
              local root = vim.fn.findfile("jest.config.ts", path .. ";")
              if root ~= "" then return root end
              return vim.fn.findfile("jest.config.js", path .. ";")
            end,
            env = { CI = "true" },
            cwd = function() return vim.fn.getcwd() end,
          }),

          -- ── Vitest ───────────────────────────────────────────────────
          require("neotest-vitest"),

          -- ── Go ───────────────────────────────────────────────────────
          require("neotest-go"),
        },

        -- ── Output configuration ──────────────────────────────────────
        output = {
          open_on_run = "short",  -- auto-open output for failures
        },

        -- ── Status column icons ───────────────────────────────────────
        icons = {
          passed    = " ",
          running   = " ",
          failed    = " ",
          skipped   = "○",
          unknown   = "?",
          watching  = "",
        },

        -- ── Summary panel ─────────────────────────────────────────────
        summary = {
          animated = true,
          follow   = true,  -- auto-follow running test
          expand_errors = true,
        },

        -- ── Diagnostic integration ────────────────────────────────────
        diagnostic = {
          enabled = true,
          severity = vim.diagnostic.severity.ERROR,
        },

        status = {
          virtual_text = true,
          signs        = true,
        },
      })
    end,
  },
}
```

---

## Python: pytest

### Project Structure

```
project/
├── src/
│   └── myapp/
│       └── utils.py
├── tests/
│   ├── conftest.py
│   └── test_utils.py
├── pyproject.toml
└── pytest.ini
```

### pytest.ini / pyproject.toml

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths     = ["tests"]
addopts       = "-v --tb=short"
python_files  = "test_*.py *_test.py"
python_classes = "Test*"
python_functions = "test_*"
```

### conftest.py patterns

```python
# tests/conftest.py
import pytest
from django.test import TestCase

@pytest.fixture(scope="session")
def django_db_setup():
    """Reuse the same DB across the session."""
    pass

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()
```

---

## JavaScript: Jest

### jest.config.ts

```typescript
import type { Config } from "jest";

const config: Config = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/src"],
  testMatch: ["**/__tests__/**/*.ts", "**/*.test.ts"],
  collectCoverageFrom: ["src/**/*.ts", "!src/**/*.d.ts"],
  coverageReporters: ["text", "lcov"],
};

export default config;
```

---

## JavaScript: Vitest

### vitest.config.ts

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "jsdom",   // or "node"
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
    },
  },
});
```

---

## Debug Tests with DAP

The `<leader>td` keymap runs the nearest test in DAP debug mode (breakpoints work):

```lua
-- Ensure the Python DAP adapter is configured (see 16-debugging.md)
-- For Jest, configure the node-debug2 adapter
require("dap").adapters["pwa-node"] = {
  type = "server",
  host = "localhost",
  port = "${port}",
  executable = {
    command = "node",
    args = { "path/to/js-debug/src/dapDebugServer.js", "${port}" },
  },
}
```

---

## Coverage

### Python (pytest-cov)

```bash
pip install pytest-cov
pytest --cov=src --cov-report=term-missing
```

### JavaScript (built-in or c8)

```bash
npx vitest --coverage
npx jest --coverage
```

### Visualize coverage in Neovim

```lua
{
  "andythigpen/nvim-coverage",
  config = function()
    require("coverage").setup({
      commands = true,
      highlights = {
        covered   = { fg = "#C3E88D" },
        uncovered = { fg = "#F07178" },
        partial   = { fg = "#FFCB6B" },
      },
    })
  end,
  keys = {
    { "<leader>cv",  "<cmd>Coverage<CR>",       desc = "Load coverage" },
    { "<leader>ct",  "<cmd>CoverageToggle<CR>", desc = "Toggle coverage highlights" },
    { "<leader>cs",  "<cmd>CoverageSummary<CR>",desc = "Coverage summary" },
  },
}
```

---

## Key Mappings Reference

| Keymap        | Action                                |
|---------------|---------------------------------------|
| `<leader>tt`  | Run nearest test                      |
| `<leader>tf`  | Run current test file                 |
| `<leader>tl`  | Re-run last test                      |
| `<leader>ts`  | Run entire test suite                 |
| `<leader>tw`  | Watch test file (auto re-run)         |
| `<leader>td`  | Debug nearest test (DAP)              |
| `<leader>to`  | Open test output                      |
| `<leader>tO`  | Toggle output panel                   |
| `<leader>tS`  | Toggle summary panel                  |
| `]t`          | Jump to next failed test              |
| `[t`          | Jump to previous failed test          |
| `<leader>cv`  | Load and show coverage                |
| `<leader>ct`  | Toggle coverage highlights            |

---

## Troubleshooting

### Neotest can't find tests

```vim
:lua require("neotest").summary.open()
-- Check that the adapter recognises the file
:lua require("neotest").run.run({ vim.fn.expand("%"), strategy = "integrated" })
```

### pytest not finding virtual env

```bash
# Activate first, then open Neovim
source .venv/bin/activate && nvim .
# Or ensure the adapter python path is set correctly
```

### Jest output is empty

```vim
-- Check jest is installed and the config file is detected
:lua print(vim.fn.system("npx jest --listTests"))
```

---

## Next Steps

1. [File Navigation](./18-file-navigation.md)
2. [Themes & UI](./19-themes-ui.md)
