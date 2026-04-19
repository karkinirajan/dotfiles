# NoSQL Database Development

## MongoDB Support

```lua
-- lua/plugins/mongodb.lua
return {
  -- MongoDB syntax
  {
    "kongo2002/vim-mongo",
    ft = { "javascript", "typescript", "mongo" },
  },

  -- Database UI (supports MongoDB)
  {
    "kristijanhusak/vim-dadbod-ui",
    dependencies = {
      "tpope/vim-dadbod",
    },
  },
}
```

## MongoDB Connections

```lua
vim.g.dbs = {
  {
    name = "local_mongo",
    url = "mongodb://localhost:27017/mydb",
  },
  {
    name = "atlas_mongo",
    url = "mongodb+srv://user:pass@cluster.mongodb.net/mydb",
  },
}
```

## Redis Integration

```lua
-- lua/plugins/redis.lua
return {
  -- Redis support via dadbod
  {
    "tpope/vim-dadbod",
    config = function()
      vim.g.dbs = vim.tbl_extend("force", vim.g.dbs or {}, {
        { name = "local_redis", url = "redis://localhost:6379" },
      })
    end,
  },
}
```

## Mongoose Snippets (MongoDB + Node.js)

```lua
local ls = require("luasnip")
ls.add_snippets("javascript", {
  ls.snippet("mongoose_schema", {
    ls.text_node({
      "const mongoose = require('mongoose');",
      "",
      "const schema = new mongoose.Schema({",
      "  ",
    }),
    ls.insert_node(1, "field: String"),
    ls.text_node({
      "",
      "}, { timestamps: true });",
      "",
      "module.exports = mongoose.model('",
    }),
    ls.insert_node(2, "Model"),
    ls.text_node("', schema);"),
  }),
})
```

## Next Steps

- [Docker Integration](./11-docker.md)
- [Kubernetes Setup](./12-kubernetes.md)
