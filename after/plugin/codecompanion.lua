require("codecompanion").setup({
  strategies = {
    chat = { adapter = "deepseek" },
    inline = { adapter = "deepseek" },
  },
  adapters = {
    deepseek = function()
      return require("codecompanion.adapters").extend("deepseek", {
        env = {
          api_key = "cmd:echo $ANTHROPIC_AUTH_TOKEN",   -- 推荐放环境变量
          -- api_key = "sk-xxx"                    -- 或直接写（不推荐）
        },
        schema = {
          model = { default = "deepseek-chat" },    -- V3，代码用 deepseek-coder 也可
          temperature = { default = 0.3 },
          max_tokens = { default = 8192 },
        },
      })
    end,
  },
  display = {
    chat = { window = { width = 0.55, height = 0.85, border = "rounded" } },
  },
})

vim.keymap.set("n", "<leader>ac", "<cmd>CodeCompanionChat<cr>",  { desc = "DeepSeek Chat" })
vim.keymap.set("v", "<leader>ai", "<cmd>CodeCompanionInline<cr>", { desc = "DeepSeek Inline" })
