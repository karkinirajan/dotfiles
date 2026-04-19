# Docker Integration

## Docker Plugin

```lua
-- lua/plugins/docker.lua
return {
  {
    "azratul/devops-tools.nvim",
    dependencies = {
      "nvim-telescope/telescope.nvim",
      "nvim-lua/plenary.nvim",
    },
    keys = {
      { "<leader>Do", "<cmd>DevopsTools<cr>", desc = "DevOps Tools" },
      { "<leader>Dc", "<cmd>DevopsContainers<cr>", desc = "Docker Containers" },
      { "<leader>Di", "<cmd>DevopsImages<cr>", desc = "Docker Images" },
    },
    opts = {
      docker = {
        enable = true,
      },
    },
  },
}
```

## LSP for Dockerfiles

```lua
-- Install Docker LSP
:MasonInstall dockerls docker_compose_language_service hadolint
```

```lua
-- lua/plugins/lsp.lua (add to ensure_installed)
ensure_installed = {
  "dockerls",                        -- Dockerfile
  "docker_compose_language_service", -- docker-compose.yml
}
```

## Docker Compose Support

```lua
-- lua/plugins/docker.lua (add)
return {
  -- Docker Compose
  {
    "jamestthompson3/nvim-remote-containers",
    config = function()
      require("devcontainers").setup({})
    end,
  },
}
```

## Dockerfile Syntax & Linting

```lua
-- lua/plugins/linting.lua
linters_by_ft = {
  dockerfile = { "hadolint" },
}
```

## Keybindings

```lua
-- lua/config/keymaps.lua
vim.keymap.set("n", "<leader>db", ":!docker build -t ", { desc = "Docker build" })
vim.keymap.set("n", "<leader>dr", ":!docker run ", { desc = "Docker run" })
vim.keymap.set("n", "<leader>dc", ":!docker-compose up -d<CR>", { desc = "Docker Compose up" })
vim.keymap.set("n", "<leader>dd", ":!docker-compose down<CR>", { desc = "Docker Compose down" })
```

## Next Steps

- [Kubernetes Setup](./12-kubernetes.md)
- [Terraform Configuration](./13-terraform.md)
