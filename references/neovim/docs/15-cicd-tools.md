# CI/CD Tools in Neovim

## Overview

This guide covers Neovim support for CI/CD configuration and related DevOps files:

| Tool              | What's Covered                              |
|-------------------|---------------------------------------------|
| GitHub Actions    | YAML syntax, LSP, lint, schema validation   |
| GitLab CI         | `.gitlab-ci.yml` schema support             |
| Jenkins           | Groovy LSP for Jenkinsfile                  |
| Docker            | Dockerfile LSP and linting (hadolint)       |
| YAML              | General YAML LSP (`yamlls`) with schemas    |
| Shell scripts     | `bashls`, `shfmt`, `shellcheck`             |
| JSON Schemas      | SchemaStore integration                     |

---

## YAML LSP with Schema Validation

The `yaml-language-server` supports JSON Schema for automatic validation and completion.

### yamlls Setup

```lua
-- In your mason-lspconfig setup_handlers:
["yamlls"] = function()
  lspconfig.yamlls.setup({
    capabilities = capabilities,
    settings = {
      yaml = {
        -- Enable schema validation
        validate    = true,
        hover       = true,
        completion  = true,
        format      = { enable = true },

        -- Schema mappings (URL -> file patterns)
        schemas = {
          -- GitHub Actions
          ["https://json.schemastore.org/github-workflow.json"] = ".github/workflows/*.{yml,yaml}",
          ["https://json.schemastore.org/github-action.json"]   = ".github/actions/**/action.{yml,yaml}",

          -- GitLab CI
          ["https://gitlab.com/gitlab-org/gitlab/-/raw/master/app/assets/javascripts/editor/schema/ci.json"] = ".gitlab-ci.yml",

          -- Docker Compose
          ["https://raw.githubusercontent.com/compose-spec/compose-spec/master/schema/compose-spec.json"] = "docker-compose*.{yml,yaml}",

          -- Helm values
          ["https://json.schemastore.org/helmfile.json"] = "helmfile.{yml,yaml}",

          -- Kubernetes
          ["https://raw.githubusercontent.com/yannh/kubernetes-json-schema/master/v1.30.0-standalone-strict/all.json"] = {
            "k8s/**/*.{yml,yaml}",
            "kubernetes/**/*.{yml,yaml}",
            "manifests/**/*.{yml,yaml}",
          },

          -- Ansible
          ["https://json.schemastore.org/ansible-playbook.json"] = "playbooks/**/*.{yml,yaml}",
          ["https://json.schemastore.org/ansible-role-2.9.json"] = "roles/**/{tasks,handlers,vars,defaults,meta}/*.{yml,yaml}",
        },

        -- Schemas from SchemaStore (broad coverage)
        schemaStore = {
          enable = false,  -- Managed manually above (or use SchemaStore plugin below)
          url    = "https://www.schemastore.org/api/json/catalog.json",
        },
      },
    },
  })
end,
```

### Auto-detect Schemas with SchemaStore Plugin

```lua
{
  "b0o/schemastore.nvim",
  -- No config needed; used inside yamlls and jsonls setups
}

-- Then in yamlls setup:
schemas = require("schemastore").yaml.schemas(),
```

---

## GitHub Actions

### Treesitter parser

```lua
-- Add to ensure_installed in treesitter config:
"yaml",
```

### Useful snippets for `.github/workflows/`

Create `~/.config/nvim/snippets/yaml.lua`:

```lua
local ls  = require("luasnip")
local s   = ls.snippet
local t   = ls.text_node
local i   = ls.insert_node
local fmt = require("luasnip.extras.fmt").fmt

return {
  -- GitHub Actions: basic workflow
  s("gha-workflow", fmt([[
name: {}

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  {}:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: {}
        run: {}
]], { i(1, "CI"), i(2, "build"), i(3, "Set up"), i(4, "echo hello") })),
}
```

---

## GitLab CI

Add the schema as above in `yamlls`. Completion and validation will work
automatically in `.gitlab-ci.yml`.

---

## Shell Script LSP (bashls + shellcheck)

### Installation via Mason

```vim
:MasonInstall bash-language-server shellcheck shfmt
```

### LSP configuration

```lua
["bashls"] = function()
  lspconfig.bashls.setup({
    capabilities = capabilities,
    settings = {
      bashIde = {
        globPattern         = "*@(.sh|.inc|.bash|.command)",
        shellcheckPath      = "shellcheck",
        shellcheckArguments = "-x",   -- follow `source` directives
        explainshellEndpoint = "",
      },
    },
  })
end,
```

### Shellcheck linting via nvim-lint

```lua
lint.linters_by_ft = {
  sh   = { "shellcheck" },
  bash = { "shellcheck" },
}
```

### shfmt formatting via conform.nvim

```lua
formatters_by_ft = {
  sh   = { "shfmt" },
  bash = { "shfmt" },
}

-- shfmt options:
formatters = {
  shfmt = {
    prepend_args = { "-i", "2", "-ci" },  -- 2-space indent, switch-case indent
  },
}
```

---

## JSON Schema Validation

```lua
["jsonls"] = function()
  lspconfig.jsonls.setup({
    capabilities = capabilities,
    settings = {
      json = {
        schemas  = require("schemastore").json.schemas(),
        validate = { enable = true },
      },
    },
  })
end,
```

This automatically validates `.eslintrc.json`, `package.json`, `tsconfig.json`, `.prettierrc`, etc.

---

## Dockerfile (see also 11-docker.md)

```lua
-- Already covered; quick summary:
-- Mason: dockerls, docker_compose_language_service, hadolint
-- Linting: hadolint for Dockerfiles
lint.linters_by_ft = {
  dockerfile = { "hadolint" },
}
```

---

## CI Output / Test Results

### Quickfix integration

When running CI locally, populate the quickfix list with errors:

```lua
-- Run a shell command and send output to quickfix
vim.keymap.set("n", "<leader>ci", function()
  vim.cmd("cexpr system('npm test 2>&1')")
  vim.cmd("copen")
end, { desc = "Run tests → quickfix" })
```

### Output to terminal split

```lua
vim.keymap.set("n", "<leader>ct", function()
  vim.cmd("botright split | terminal npm run ci")
end, { desc = "Run CI in terminal split" })
```

---

## Telescope: search workflow files

```lua
vim.keymap.set("n", "<leader>fw", function()
  require("telescope.builtin").find_files({
    search_dirs = { ".github/workflows", ".gitlab-ci.yml" },
    prompt_title = "CI/CD Files",
  })
end, { desc = "Find CI/CD files" })
```

---

## Recommended Key Mappings

| Keymap         | Action                                      |
|----------------|---------------------------------------------|
| `<leader>ci`   | Run tests and populate quickfix             |
| `<leader>ct`   | Run CI command in terminal split            |
| `<leader>fw`   | Find CI/CD workflow files                   |
| `]e` / `[e`    | Navigate errors (diagnostics)               |

---

## Troubleshooting

### Schema validation not triggering

```vim
:LspInfo    " Check if yamlls is attached
:lua print(vim.inspect(vim.lsp.get_active_clients()))
```

### SchemaStore errors

```bash
# Ensure network access; schemas are downloaded on demand
# Clear LSP cache if needed:
rm -rf ~/.local/share/nvim/lsp_servers
```

### shellcheck not finding sourced files

```bash
# Add -x flag (follow source) and set the path:
shellcheck -x ./script.sh
```

---

## Next Steps

1. [Debugging (DAP)](./16-debugging.md)
2. [Testing Integration](./17-testing.md)
