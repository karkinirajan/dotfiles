# Kubernetes Development

## Kubernetes Plugin

```lua
-- lua/plugins/kubernetes.lua
return {
  {
    "Ramilito/kubectl.nvim",
    dependencies = { "nvim-telescope/telescope.nvim" },
    keys = {
      { "<leader>k", "<cmd>Kubectl<cr>", desc = "Kubectl" },
    },
    config = function()
      require("kubectl").setup()
    end,
  },
}
```

## YAML LSP

```lua
:MasonInstall yamlls helm_ls
```

## Kubernetes Keymaps

```lua
-- lua/config/keymaps.lua
vim.keymap.set("n", "<leader>kg", ":!kubectl get ", { desc = "kubectl get" })
vim.keymap.set("n", "<leader>kd", ":!kubectl describe ", { desc = "kubectl describe" })
vim.keymap.set("n", "<leader>ka", ":!kubectl apply -f %<CR>", { desc = "kubectl apply current file" })
vim.keymap.set("n", "<leader>kl", ":!kubectl logs ", { desc = "kubectl logs" })
```

## Next Steps

- [Terraform Configuration](./13-terraform.md)
- [CI/CD Tools](./15-cicd-tools.md)
