# Terraform Configuration

## Terraform LSP

```lua
:MasonInstall terraformls tflint
```

## Terraform Plugin

```lua
-- lua/plugins/terraform.lua
return {
  {
    "hashivim/vim-terraform",
    ft = { "terraform", "tf", "hcl" },
    config = function()
      vim.g.terraform_fmt_on_save = 1
      vim.g.terraform_align = 1
    end,
  },
}
```

## Formatting & Linting

```lua
-- lua/plugins/formatting.lua
formatters_by_ft = {
  terraform = { "terraform_fmt" },
  hcl = { "terraform_fmt" },
}

-- lua/plugins/linting.lua
linters_by_ft = {
  terraform = { "tflint" },
}
```

## Keymaps

```lua
vim.keymap.set("n", "<leader>ti", ":!terraform init<CR>", { desc = "Terraform init" })
vim.keymap.set("n", "<leader>tp", ":!terraform plan<CR>", { desc = "Terraform plan" })
vim.keymap.set("n", "<leader>ta", ":!terraform apply<CR>", { desc = "Terraform apply" })
vim.keymap.set("n", "<leader>tf", ":!terraform fmt<CR>", { desc = "Terraform format" })
```
