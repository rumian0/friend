![links_status](./static/favicon.ico)

  # Links Status

  精简版友链状态检测与 RSS 文章聚合工具


## 项目简介

本项目是基于 [Friend-Circle-Lite](https://github.com/willow-god/Friend-Circle-Lite) 修改的精简版本，移除了邮件通知、合并功能等复杂特性，专注于核心功能：

- **RSS 文章抓取**：自动爬取友链 RSS，聚合最新文章
- **友链状态检测**：定时检测友链可访问性
- **简约前端展示**：卡片式布局，响应式设计
- **GitHub Actions 部署**：无需服务器，全自动运行
- **EdgeOne Makers 托管**：Actions 算数据，EdgeOne 托管与加速

## 功能特性

- RSS 文章自动抓取与聚合
- 友链可访问性检测（支持备用 API）
- 简约现代的前端展示页面
- GitHub Actions 运行，零服务器成本
- 响应式设计，适配各种设备

## 项目结构

```
.
├── .github/workflows/     # GitHub Actions 工作流
├── links_status/          # 核心代码模块
│   ├── __init__.py        # 请求头配置
│   ├── all_friends.py     # RSS 抓取处理
│   ├── link_status.py     # 友链状态检测
│   └── utils/             # 工具函数
├── static/                # 静态文件
│   ├── index.html         # 前端展示页面
│   ├── edgeone.json       # EdgeOne Makers 的 headers 配置
│   └── favicon.ico
├── EDGEONE.md             # EdgeOne 部署完整步骤
├── conf.yaml              # 配置文件
└── run.py                 # 主入口
```

> `all.json` / `status.json` / `errors.json` 由 Actions 每次运行时生成，
> 再和 `static/` 一起打包成 `pages/` 目录部署出去，因此不在仓库里。

## 快速开始

### 1. Fork 仓库

点击右上角 Fork 按钮，将仓库复制到你的 GitHub 账号下。

### 2. 配置权限

进入仓库 `Settings` -> `Actions` -> `General`，拉到最下方，勾选 **Read and write permissions**，保存。

### 3. 修改配置

编辑 `conf.yaml` 文件：

```yaml
# 爬虫配置
spider_settings:
  enable: true
  json_url: "https://your-domain.com/friend.json"  # 你的友链 JSON 地址
  article_count: 5                                   # 每个友链保留文章数

# 友链状态检测
link_status:
  enable: true
  timeout: 30
  max_attempts: 3
  use_backup_api: true
  backup_api_urls:
    - "https://v1.nsuuu.com/api/netCheck"
    - "https://v1.nsuuu.com/api/status"
```

### 4. 运行 Action

进入 `Actions` 页面，手动运行 workflow，或等待定时触发（默认每 6 小时一次）。

> **注意**：即使友链 JSON 文件无法访问或程序运行出错，GitHub Actions 也不会发送失败邮件通知。工作流会自动创建空数据文件并继续执行，你可以通过查看 Actions 日志了解详细情况。

### 5. 部署页面

默认部署到 **EdgeOne Makers**（腾讯云 EdgeOne 的静态托管 + 加速）：

1. 在 [EdgeOne Makers 控制台](https://console.tencentcloud.com/edgeone/makers) 创建 API Token；
2. 在仓库 `Settings → Secrets and variables → Actions` 里新增 Secret `EDGEONE_API_TOKEN`；
3. 运行 workflow，产物会自动部署到项目 `friend-links`（可用仓库变量 `EDGEONE_PROJECT_NAME` 改名）。

完整步骤（含域名绑定、双写过渡、排错）见 **[EDGEONE.md](./EDGEONE.md)**。

> 未配置 `EDGEONE_API_TOKEN` 时，工作流会跳过这一步，继续走 `page` 分支的旧链路，不会报错。

也可以继续用 GitHub Pages 或任意静态托管服务部署 `static` 目录（配合生成出来的 json）。

## 友链 JSON 格式

你的友链页面需要提供如下格式的 JSON：

```json
{
  "friends": [
    ["站点名称", "https://example.com", "https://example.com/avatar.png"],
    ["站点名称2", "https://example2.com", "https://example2.com/avatar.png"]
  ]
}
```

## 配置说明

### spider_settings

| 参数 | 说明 |
|-----|------|
| `enable` | 是否启用文章抓取 |
| `json_url` | 友链 JSON 文件地址 |
| `article_count` | 每个友链抓取的文章数量 |

### link_status

| 参数 | 说明 |
|-----|------|
| `enable` | 是否启用友链状态检测 |
| `timeout` | 请求超时时间（秒） |
| `max_attempts` | 最大重试次数 |
| `use_backup_api` | 是否使用备用 API 检测 |
| `backup_api_urls` | 备用 API 地址列表 |

## 本地预览

```bash
# 进入项目目录
cd links-pyq-status-main

# 使用 Python 启动本地服务器
python -m http.server 8080

# 访问 http://localhost:8080/static/
```

## 技术栈

- **后端**: Python 3.x + requests + aiohttp + feedparser
- **前端**: 原生 HTML + CSS + JavaScript
- **调度**: GitHub Actions（每 6 小时）
- **托管**: EdgeOne Makers（产物由 Actions 直接部署）

## 已知问题

- 友链检测曾因请求头声明 `br` 压缩但未安装 Brotli，导致大量正常站点被判为不可访问，已修复。
- `conf.yaml` 里的备用检测 API（`v1.nsuuu.com`）目前返回 502 已失效，仅作兜底，可自行替换或关闭。

## 许可证

MIT License

## 致谢

- 原项目 [Friend-Circle-Lite](https://github.com/willow-god/Friend-Circle-Lite) by willow-god
