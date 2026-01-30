# Debugging with DAP

## Core DAP Plugins

```lua
-- lua/plugins/dap.lua
return {
  -- DAP Core
  {
    "mfussenegger/nvim-dap",
    dependencies = {
      "rcarriga/nvim-dap-ui",
      "nvim-neotest/nvim-nio",
      "theHamsta/nvim-dap-virtual-text",
    },
    keys = {
      { "<F5>", "<cmd>lua require('dap').continue()<cr>", desc = "Continue" },
      { "<F10>", "<cmd>lua require('dap').step_over()<cr>", desc = "Step Over" },
      { "<F11>", "<cmd>lua require('dap').step_into()<cr>", desc = "Step Into" },
      { "<F12>", "<cmd>lua require('dap').step_out()<cr>", desc = "Step Out" },
      { "<leader>b", "<cmd>lua require('dap').toggle_breakpoint()<cr>", desc = "Toggle Breakpoint" },
      { "<leader>dr", "<cmd>lua require('dap').repl.open()<cr>", desc = "REPL" },
    },
    config = function()
      local dap, dapui = require("dap"), require("dapui")

      -- UI Setup
      dapui.setup()
      require("nvim-dap-virtual-text").setup()

      -- Auto-open UI
      dap.listeners.after.event_initialized["dapui_config"] = function()
        dapui.open()
      end
      dap.listeners.before.event_terminated["dapui_config"] = function()
        dapui.close()
      end
      dap.listeners.before.event_exited["dapui_config"] = function()
        dapui.close()
      end

      -- Signs
      vim.fn.sign_define('DapBreakpoint', { text='🔴', texthl='', linehl='', numhl='' })
      vim.fn.sign_define('DapStopped', { text='▶️', texthl='', linehl='', numhl='' })
    end,
  },

  -- Python DAP
  {
    "mfussenegger/nvim-dap-python",
    ft = "python",
    config = function()
      require("dap-python").setup(vim.fn.stdpath("data") .. "/mason/packages/debugpy/venv/bin/python")
    end,
  },

  -- JavaScript/TypeScript DAP
  {
    "mxsdev/nvim-dap-vscode-js",
    ft = { "javascript", "typescript", "javascriptreact", "typescriptreact" },
    dependencies = {
      {
        "microsoft/vscode-js-debug",
        build = "npm install --legacy-peer-deps && npx gulp vsDebugServerBundle && mv dist out"
      },
    },
    config = function()
      require("dap-vscode-js").setup({
        debugger_path = vim.fn.stdpath("data") .. "/lazy/vscode-js-debug",
        adapters = { "pwa-node", "pwa-chrome", "node-terminal" },
      })

      for _, language in ipairs({ "typescript", "javascript" }) do
        require("dap").configurations[language] = {
          {
            type = "pwa-node",
            request = "launch",
            name = "Launch file",
            program = "${file}",
            cwd = "${workspaceFolder}",
          },
          {
            type = "pwa-node",
            request = "attach",
            name = "Attach",
            processId = require("dap.utils").pick_process,
            cwd = "${workspaceFolder}",
          },
        }
      end
    end,
  },
}
```

## Usage

1. Set breakpoint: `<leader>b`
2. Start debugging: `<F5>`
3. Step over: `<F10>`
4. Step into: `<F11>`
5. Step out: `<F12>`
