# SQL Database Development

## LSP Servers

```vim
:MasonInstall sqlls sqlfmt
```

## Database Plugins

```lua
-- lua/plugins/database.lua
return {
  -- Database UI
  {
    "kristijanhusak/vim-dadbod-ui",
    dependencies = {
      { "tpope/vim-dadbod" },
      { "kristijanhusak/vim-dadbod-completion" },
    },
    cmd = { "DBUI", "DBUIToggle", "DBUIAddConnection" },
    keys = {
      { "<leader>db", "<cmd>DBUIToggle<cr>", desc = "Database UI" },
    },
    init = function()
      vim.g.db_ui_use_nerd_fonts = 1
      vim.g.db_ui_show_database_icon = 1
      vim.g.db_ui_force_echo_notifications = 1
      vim.g.db_ui_win_position = "left"
      vim.g.db_ui_winwidth = 40

      -- Save connections
      vim.g.db_ui_save_location = vim.fn.stdpath("data") .. "/db_ui"
    end,
  },

  -- SQL LSP
  {
    "nanotee/sqls.nvim",
    ft = { "sql", "mysql", "plsql" },
    config = function()
      require("lspconfig").sqls.setup({
        on_attach = function(client, bufnr)
          require("sqls").on_attach(client, bufnr)
        end,
        settings = {
          sqls = {
            connections = {
              {
                driver = "postgresql",
                dataSourceName = "host=127.0.0.1 port=5432 user=postgres dbname=mydb sslmode=disable",
              },
              {
                driver = "mysql",
                dataSourceName = "root:root@tcp(127.0.0.1:3306)/mydb",
              },
              {
                driver = "sqlite3",
                dataSourceName = "file:./db.sqlite",
              },
            },
          },
        },
      })
    end,
  },

  -- Alternative: dbout.nvim (modern)
  {
    "zongben/dbout.nvim",
    cmd = { "Dbout" },
    build = "npm install",
    dependencies = {
      "nvim-telescope/telescope.nvim",
      "nvim-lua/plenary.nvim",
    },
    config = function()
      require("dbout").setup({})
    end,
  },
}
```

## Database Connections

### PostgreSQL

```lua
-- In your project's .env or connections file
vim.g.dbs = {
  { name = "dev_postgres", url = "postgresql://user:password@localhost:5432/mydb" },
  { name = "prod_postgres", url = "postgresql://user:password@prod.server:5432/mydb" },
}
```

### MySQL

```lua
vim.g.dbs = {
  { name = "dev_mysql", url = "mysql://user:password@localhost:3306/mydb" },
}
```

### SQLite

```lua
vim.g.dbs = {
  { name = "local_sqlite", url = "sqlite:///path/to/database.db" },
}
```

## SQL Autocompletion

```lua
-- lua/plugins/completion.lua (add to sources)
vim.api.nvim_create_autocmd("FileType", {
  pattern = { "sql", "mysql", "plsql" },
  callback = function()
    require("cmp").setup.buffer({
      sources = {
        { name = "vim-dadbod-completion" },
        { name = "buffer" },
      },
    })
  end,
})
```

## SQL Keymaps

```lua
-- lua/config/keymaps.lua
vim.keymap.set("n", "<leader>db", "<cmd>DBUIToggle<cr>", { desc = "Database UI" })
vim.keymap.set("v", "<leader>de", ":<C-u>'<,'>DBExecVisualSQL<cr>", { desc = "Execute SQL" })
vim.keymap.set("n", "<leader>ds", "<cmd>DBUIFindBuffer<cr>", { desc = "Find DB buffer" })
vim.keymap.set("n", "<leader>dr", "<cmd>DBUIRenameBuffer<cr>", { desc = "Rename DB buffer" })
vim.keymap.set("n", "<leader>dl", "<cmd>DBUILastQueryInfo<cr>", { desc = "Last query info" })
```

## SQL Formatting

```lua
-- lua/plugins/formatting.lua
formatters_by_ft = {
  sql = { "sqlfmt", "sql_formatter" },
  mysql = { "sqlfmt" },
  plsql = { "sqlfmt" },
}
```

## Usage Workflows

### 1. Connect to Database

```vim
:DBUIToggle
" Navigate to database
" Press <CR> to expand
" Navigate to tables
```

### 2. Execute Query

```vim
" In SQL buffer
:normal viw
:'<,'>DBExecVisualSQL

" Or select text visually and:
<leader>de
```

### 3. Schema Exploration

- Navigate with `hjkl`
- `<CR>` - Expand/collapse
- `o` - Open in new tab
- `d` - Delete connection
- `R` - Refresh
- `A` - Add connection
- `S` - Toggle schemas
- `?` - Help

## Project-Specific Config

```lua
-- .nvim.lua in project root
vim.g.dbs = {
  {
    name = "project_db",
    url = "postgresql://user:pass@localhost:5432/project_db"
  },
}
```

## SQL Snippets

```lua
local ls = require("luasnip")
ls.add_snippets("sql", {
  ls.snippet("select", {
    ls.text_node("SELECT "),
    ls.insert_node(1, "columns"),
    ls.text_node(" FROM "),
    ls.insert_node(2, "table"),
    ls.text_node(" WHERE "),
    ls.insert_node(3, "condition"),
    ls.text_node(";"),
  }),
})
```

## Next Steps

- [NoSQL Databases](./10-nosql-databases.md)
- [Docker Integration](./11-docker.md)
