# Neovim 个性化配置

一套高度定制化的 Neovim 配置，专注于编程效率、多语言支持和高级文本操作。

## 环境要求

### 系统依赖

| 依赖 | 用途 |
|------|------|
| **Neovim** (>= 0.5) | 核心编辑器 |
| **Python 3.11+** | 补全服务、输入法、脚本 |
| **git** | 版本控制集成 (vim-fugitive) |
| **ripgrep (rg)** | 快速搜索、Xearch、文件导航 |
| **fzf** | 模糊查找集成 |
| **ctags** | 标签生成 (Gutentags) |
| **sqlfluff** | SQL 语法检查和格式化 |
| **openpyxl** | Excel 文件处理 (xl-script) |

### Python 虚拟环境

配置预期在 `~/.venv/bin/python3` 有一个 Python 虚拟环境用于 UltiSnips：

```bash
python3 -m venv ~/.venv
~/.venv/bin/pip install pynvim
```

### 词典文件

自动补全依赖系统词典：

- `/usr/share/dict/en` - 英语
- `/usr/share/dict/esp` - 西班牙语
- `/usr/share/dict/ngerman` - 德语

### 外部程序

- **msedge.exe** - Web 搜索集成（WSL 环境）
- **wslview** - WSL 中打开 URL
- **hexdump** - 字符编码工具

## 插件管理器

使用 [vim-plug](https://github.com/junegunn/fzf.vim) 管理插件。安装插件：

```vim
:PlugInstall
```

## 已安装插件

| 插件 | 功能 |
|------|------|
| SirVer/ultisnips | 代码片段引擎 |
| junegunn/fzf + fzf.vim | 模糊查找 |
| tpope/vim-fugitive | Git 集成 |
| neovim/nvim-lspconfig | LSP 配置 |
| mason.nvim + mason-lspconfig | LSP 服务器管理 |
| mhinz/vim-signify | Git 差异标记 |
| preservim/nerdtree | 文件树 |
| voldikss/vim-floaterm | 浮动终端 |
| kevinhwang91/nvim-bqf | QuickFix 增强 |
| andymass/vim-matchup | 括号匹配增强 |
| wellle/context.vim | 上下文显示 |
| unblevable/quick-scope | 单字符跳转高亮 |
| tpope/vim-commentary | 快速注释 |
| tpope/vim-obsession | Session 保存 |
| rhysd/git-messenger.vim | Git 行历史 |
| ludovicchabant/vim-gutentags | 自动 ctags 管理 |
| mattn/emmet-vim | HTML/CSS 快捷输入 |
| mechatroner/rainbow_csv | CSV 彩虹高亮 |
| luochen1990/rainbow | 括号彩虹括号 |
| mbbill/undotree | 撤销树 |
| vim-devicons | 文件图标 |
| wilder.nvim | 命令行补全 |
| leap.nvim | 快速跳转 |
| vim-easy-align | 文本对齐 |
| targets.vim + textobj-user | 文本对象扩展 |

## 核心特色功能

### OmniJump 万能跳转模式 (`<leader>j`)

一套统一的导航系统，在不同场景下复用 `hjkl` 键：

| 模式 | 说明 | j | k | h | l |
|------|------|---|---|---|---|
| **n** | 普通模式 | 下 | 上 | 左 | 右 |
| **m** | 标记 | 下一个标记 | 上一个标记 | - | - |
| **F** | 文件系统 | 下一个文件 | 上一个文件 | - | - |
| **q** | QuickFix | 下一项 | 上一项 | - | - |
| **d** | 差异/Signify | 下一个差异 | 上一个差异 | 前窗口 | 后窗口 |
| **w** | 窗口缩放 | 缩小高度 | 增大高度 | 缩小宽度 | 增大宽度 |
| **c** | Git 冲突 | 下一冲突 | 上一冲突 | 接受传入 | 接受当前 |
| **r** | Roadmap | 下一个锚点 | 上一个锚点 | - | - |
| **s** | 滚动 | 向下滚 | 向上滚 | 向左滚 | 向右滚 |

按 `<leader>j` 进入模式选择，再按对应字母选择模式。

### Roadmap 路线图 (`:Roadmap`)

侧边栏面板，实时显示当前文件的：
- 所有标记（本地/全局）
- Git 差异行
- QuickFix 项
- 扩展标记（ExtMark）
- 当前行位置指示

### 垂直范围选择（Vertical Quick Scope）

使用 `d`、`y`、`c`、`=`、`zf`、`V`、`<C-v>` 时，光标列会显示垂直行号，方便精确选择范围。

### 增强标记系统

- `m` - 交互式放置标记，自动显示可用标记列表
- 本地标记（`a-z`）显示 `󰉁` 符号
- 全局标记（`A-Z`）显示 `` 符号
- QuickFix 标记显示 `󰙒` 符号
- 标记符号在行号旁实时显示
- `:DMarks` - 删除标记

### FZF 模糊查找集成

| 快捷键 | 功能 |
|--------|------|
| `<leader>l` | 跨文件搜索行 |
| `,l` | 当前缓冲区搜索行 |
| `,b` | 切换缓冲区 |
| `,db` | 删除缓冲区 |
| `<leader>m` | 列出标记 |
| `<c-p>` | 剪切历史选择 |
| `,c` | 命令历史 |
| `<leader>o` | Hiraishin 文件搜索 |

### 代码补全系统

- **多语言支持**：英语、德语、西班牙语、日语、中文
- **LSP 集成**：自动查询 LSP 服务器获取补全候选
- **分页浏览**：`<M-,>` / `<M-.>` 翻页
- **快速选择**：`j2`-`j9` 按编号选择候选
- **剪切历史**：所有 yank 内容自动记录可搜索

### 代码片段（UltiSnips）

| 快捷键 | 功能 |
|--------|------|
| `<C-x><C-j>` | 展开片段 |
| `<C-k>` | 向前跳转 |
| `<C-j>` | 向后跳转 |
| `<C-l>` | 展开 / 跳转 / 匿名展开 |
| `<A-l>` | FZF 片段选择器 |
| `<F4>` | 编辑片段文件 |

片段定义在 `mycoolsnippets/` 目录，支持 C、Java、Python、JavaScript、SQL、AWK、Vim、HTML、XML 等语言。

### 日语/中文输入法

内置输入法集成：

- `jJ` - 切换日语输入法（罗马字转平假名）
- `jc` - 切换中文输入法
- `jD` / `jE` - 切换德语/英语偏好
- 不同输入法状态光标行颜色不同
- 候选词列表支持分页

### Git 工作流（vim-fugitive）

| 命令 | 功能 |
|------|------|
| `:gi` | Git 状态 |
| `:gl` | Git 日志（格式化） |
| `:glg` | Git 日志（图形化） |
| `:glga` | Git 日志（全部分支） |
| `:glp` | Git 日志（带差异） |
| `:gb` | Git 分支 |
| `:gbd` | 删除分支（fzf 选择） |
| `:gco` | 切换分支（fzf 选择） |
| `:gcmt` | Git blame |
| `:gpl` / `:gps` | 拉取 / 推送（异步） |
| `:gc` / `:gca` | 提交 / 修正提交 |

### 搜索与替换

| 快捷键 | 功能 |
|--------|------|
| `s` / 可视模式 `s` | 包围文本（括号、引号等） |
| `S` | 移除包围符号 |
| `r` / 可视模式 `r` | 用寄存器内容替换 |
| `,r` / 可视模式 `,r` | 从剪切历史选择替换 |
| `,,<Tab>` | 大小写转换（驼峰转下划线） |
| `,e` | 执行 Python 表达式 |
| `,,e` | 执行 Python 代码段 |
| `,F` | QuickFix 搜索单词 |
| `,,F` | QuickFix 搜索（无词界） |

### SQL 开发

- `,,s` - SQL 语法检查操作符（配合 sqlfluff）
- `:SQLint` - 对当前文件运行 SQL lint
- 检查结果以虚拟文本形式显示在行末
- 支持自定义配置文件路径

### AWK 集成

- `:aa` - AWK 处理整个文件
- `,a` - AWK 操作符（范围选择处理）
- `:an` - AWK 结果输出到新临时文件
- `:anr` - AWK 结果以动态模式打开
- `:ar` - AWK 范围处理
- `:ae` / `:aef` - 编辑 AWK 模板 / 函数库
- 自动显示 FS（字段分隔符）信息

### LaTeX 支持

- 保存时自动编译
- 状态栏显示 PDF 页码
- 自定义语法和高亮
- 折叠支持

### 大文件支持（动态读取）

`:DyOpen` - 分块打开超大文件，按需加载内容：
- 支持数百万行文件的虚拟行号
- 动态缓冲区内标记和导航
- `:DyLocate <行号>` - 跳转到指定行
- `:MDyOpen` - 智能打开大文件

### 状态栏与标签栏

自定义状态栏显示：
- 文件路径、文件类型、编码、换行符格式
- Git 状态、异步任务指示器
- 输入法状态、语言偏好
- QuickFix 标记、扩展标记
- 位置信息（虚拟列、字节索引、百分比）

标签栏显示：
- 各标签页的缓冲区名称
- 异步任务运行状态
- Git 状态
- 输入法状态

### 转写模式

`,<Tab>i` - 进入转写模式：
- `,<Tab>g` - 希腊语模式
- `,<Tab>l` - 拉丁语模式
- 实时预览转换结果
- 自动缓存和显示

### 浮动终端

- `,T` 后按 `n` - 新建终端
- `,T` 后按 `c` - 在当前目录新建终端
- `<A-h/j/k/l>` - 任意模式下切换窗口
- `,q` - 退出终端

### 其他实用功能

| 快捷键/命令 | 功能 |
|-------------|------|
| `<F5>` | 快速运行（vim: 执行, tex: 编译, python: 运行, c: 编译） |
| `jk` | 退出到普通模式 |
| `jK` | 退出到普通模式（保留输入法状态） |
| `;` | 命令行模式（替代 `:`） |
| `<A-u>` / `<A-i>` | 上下移动行 |
| `,,s` / `,,u` | 排序去重 |
| `:QfEdit` | 编辑 QuickFix 条目，可回写到源文件 |
| `:FreezeLeft` | 分割窗口并固定左侧 |
| `:CTailBlank` / `:CHeadBlank` | 清除行尾/行首空白 |
| `:CEmptyLine` | 清除空行 |
| `:EdXl` | 编辑 Excel 处理脚本 |
| `:Notepad` | 在 Windows 记事本中打开（WSL） |
| `:WinLocate` | 在资源管理器中定位文件（WSL） |
| `:WSLview` | 在浏览器中打开文件（WSL） |
| `:Roadmap` | 切换路线图面板 |
| `:AuWidth` / `:AuHeight` | 自动调整窗口宽/高 |
| `:Ztool` | 打开工具文件 |
| `g=` | 文本对齐（EasyAlign） |
| `gc` | 注释行（Commentary） |
| `gC` | 反向注释 |
| `gl` | LSP 操作菜单 |
| `gt` | 跳转到标签 |

### 分屏操作

- `,s` - 垂直分屏后选择操作（打开文件/缓冲区/标签/QuickFix/终端等）
- `,S` - 水平分屏后选择操作
- `,t` / `,T` - 新标签页操作
- `,f` - 浮动窗口操作

操作符：
- `o` - 打开文件
- `b` - 切换缓冲区
- `t` - 跳转到标签
- `q` - QuickFix 项
- `m` - 扩展标记
- `T` - 终端
- `f` - 临时文件
- `g` - Git 修改文件

## 文件结构

```
init.vim                      # 主配置文件
autoload/plug.vim             # 插件管理器
syntax/                       # 自定义语法文件
  ark.vim                     # 自定义语言语法
  log.vim                     # 日志文件高亮
mycoolsnippets/               # 代码片段定义
after/                        # 文件类型覆盖
  ftplugin/tex.vim            # LaTeX 设置
lua/                          # Lua 插件
  myhealth/health.lua         # 健康检查
awk-lib/                      # AWK 函数库
tex/                          # LaTeX 宏包
training-tools/               # 语言学习爬虫
cn/                           # 中文词典和数据
jp/                           # 日语词典和数据
```

## 自定义命令

| 命令 | 说明 |
|------|------|
| `:QfSearch` | 在当前缓冲区中搜索 |
| `:QfJearch` | 搜索非 ASCII 字符 |
| `:Xearch` | 递归搜索（支持 Hiraishin 锚点） |
| `:QfAll` | 查看已保存的搜索结果 |
| `:QfYank` | 保存当前 QuickFix |
| `:QfRemove` | 删除已保存的搜索 |
| `:QfMark` | 将当前行添加到 QuickFix |
| `:Roadmap` | 切换路线图面板 |
| `:MEdit` | 智能打开缓冲区/文件 |
| `:DyOpen` | 动态打开大文件 |
| `:DyLocate` | 在动态缓冲区中定位行 |
| `:FreezeLeft` | 固定左侧分屏对比 |
| `:SQLint` | SQL 语法检查 |
| `:ChineseFZF` | 中文查找 |
| `:IndoEuropeanFZF` | 印欧语查找 |
| `:WSLview` | WSL 浏览器打开 |
| `:Notepad` | Windows 记事本打开 |
| `:WinLocate` | 资源管理器定位 |
| `:CTailBlank` | 清除行尾空白 |
| `:CHeadBlank` | 清除行首空白 |
| `:CEmptyLine` | 清除空行 |
| `:EdXl` | 编辑 Excel 脚本 |
| `:EdComplete` | 编辑补全服务 |
| `:EdAnon` | 编辑匿名展开脚本 |
