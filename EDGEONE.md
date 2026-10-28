# 部署到 EdgeOne Makers（腾讯云 EdgeOne）

本文档说明如何把本项目从「GitHub Actions + page 分支 + 腾讯云 Pages」迁移到 **EdgeOne Makers**，
并解释为什么采用这种架构。

---

## 1. 最终架构

```
GitHub Actions（每 6 小时）
   ├─ Python 跑 run.py
   │    ├─ 抓取友链 RSS  → all.json / errors.json
   │    └─ 检测友链存活   → status.json
   ├─ 组装 pages/ 目录（index.html + 3 个 json + favicon + edgeone.json）
   ├─ ① 部署到 EdgeOne Makers（npx edgeone makers deploy）   ← 新链路
   └─ ② 推送 page 分支 + 腾讯云 Pages webhook                 ← 旧链路（双写过渡期保留）
```

关键结论：

| 需求 | EdgeOne Makers 能力 | 结论 |
|------|--------------------|------|
| 跑 Python 脚本 | 支持 Python 云函数（3.10），单次最长 **120 秒** | 本项目全量跑一次约 **115 秒**，顶着上限，很危险 |
| 定时触发 | `edgeone.json` 的 `schedules`，但官方文档写明 **cron 最小间隔是一天** | 做不到 6 小时一次 |
| 直接部署静态产物 | ✅ `edgeone makers deploy <目录>` | 采用 |

所以本项目**不在 EdgeOne 上跑 Python**，而是：

> **GitHub Actions 负责「算」，EdgeOne 负责「托管 + 加速」。**

这样既能保留 6 小时一次的频率，又不用为了 120 秒上限去重写整套抓取逻辑。

---

## 2. 一次性配置（约 10 分钟）

### 2.1 开通 EdgeOne Makers

1. 打开腾讯云控制台，进入 **EdgeOne → Makers**：
   `https://console.tencentcloud.com/edgeone/makers`
2. 首次进入按提示开通服务（有免费额度）。
3. 不需要手动新建项目 —— 第一次部署时 CLI 会自动创建。

> 如果是国内站（域名已备案），控制台左上角的站点类型选「**中国站**」；
> 只有国际站可以先用 `xxx.edgeone.app` 临时域名测试。

### 2.2 创建 API Token

1. 在 Makers 控制台切到 **API Token** 标签页。
2. 点「**创建 API Token**」。
3. 填写描述（例如 `github-actions-friend`），有效期建议选 **1 年**。
4. 提交后**立即复制** Token（只显示一次）。

### 2.3 写进 GitHub 仓库 Secrets

1. 打开仓库 → **Settings → Secrets and variables → Actions**。
2. 在 **Secrets** 标签页点 **New repository secret**。
3. Name 填：`EDGEONE_API_TOKEN`
4. Secret 填：刚才复制的 Token。

### 2.4（可选）仓库变量

在同一个页面的 **Variables** 标签页，按需新增：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `EDGEONE_PROJECT_NAME` | `friend-links` | EdgeOne 项目名。想复用已有项目就填已有的名字 |
| `EDGEONE_SITE` | 空（CLI 按出口 IP 自动判断） | 填 `china` 部署到中国站；填 `global` 部署到国际站 |

> GitHub Actions 的出口 IP 在国外，**不填 `EDGEONE_SITE` 时大概率会落到国际站**。
> 域名要绑定在国内加速，请显式设置 `EDGEONE_SITE=china`（前提是域名已备案）。

### 2.5 首次部署

1. 打开仓库 **Actions → Links Status → Run workflow**。
2. 等待约 2～3 分钟。
3. 日志里出现 `Deploying ./pages to EdgeOne Makers project: ...` 且没有报错即成功。
4. 到 Makers 控制台的 **项目 → 部署记录** 里能看到新部署，并拿到一个临时访问域名。

> 没配置 `EDGEONE_API_TOKEN` 时，工作流会**跳过** EdgeOne 部署并打印一条 warning，
> 旧的 page 分支链路照常工作 —— 所以可以先改代码、后配 Token，不会把流程跑红。

---

## 3. 绑定域名

部署成功后，站点默认域名形如 `https://xxxx.edgeone.app`。要换回 `fc.mingcy.cn`：

1. Makers 控制台 → 项目 → **域名管理 → 添加自定义域名**。
2. 输入 `fc.mingcy.cn`。
3. 按提示到 DNS 服务商添加 **CNAME** 记录，指向控制台给出的目标域名。
4. 等待证书签发（通常几分钟）。
5. 验证：
   - `https://fc.mingcy.cn/` 能打开页面
   - `https://fc.mingcy.cn/status.json` 返回最新时间戳
   - `https://fc.mingcy.cn/all.json` 有 `article_data`

> **切换前先验证**：临时域名可以直接访问，先确认页面、`status.json`、`all.json` 都正常，
> 再改 DNS。首页已经改成相对路径取数，所以在临时域名下也能正常显示友链状态。

⚠️ 国内站绑定域名需要 **ICP 备案**，且备案主体与腾讯云账号一致。

---

## 4. 双写过渡期

当前工作流会**同时**更新两条链路：

| 链路 | 状态 | 说明 |
|------|------|------|
| EdgeOne Makers | 新 | 直接部署 `pages/` 目录 |
| page 分支 + 腾讯云 Pages webhook | 旧 | 过渡期保留，webhook 失败只报警不再让任务失败 |

确认 EdgeOne 稳定运行 **1～2 周**后，可以按下面步骤停掉旧链路：

1. 打开 `.github/workflows/links-status.yml`。
2. 删除这两个步骤：
   - `Publish to page branch (legacy)`
   - `Trigger Tencent Cloud Pages Webhook`
3. 可选：删除仓库里的 `page` 分支，并在腾讯云 Pages 控制台下线旧项目。
4. 「Download existing JSON files from page branch」这一步也就可以一起删了
   （它只是为了在 Python 出错时用旧数据兜底）。

---

## 5. 常见问题

### 5.1 部署报 `project not found` / 名字冲突

`-n` 指定的项目名必须**全小写、只用字母数字和连字符**。如果控制台里已经有同名但类型不同的项目
（例如 Git 关联型），CLI 无法直接部署，需要：
- 换一个 `EDGEONE_PROJECT_NAME`，或
- 在控制台新建一个「**直接上传**」类型的项目并使用它的名字。

### 5.2 部署成功但页面 404

`pages/` 目录里必须**直接**包含 `index.html`（不能在子目录里）。可以在日志的
`Assemble deploy directory → ls -la pages` 里确认。

### 5.3 数据不更新（页面还是旧的）

`static/edgeone.json` 里已经为所有路径加了：

```json
{ "key": "Cache-Control", "value": "no-cache, max-age=0, must-revalidate" }
```

如果仍然不更新，检查是否命中了浏览器缓存，或确认域名解析到的是**最新部署**。

### 5.4 友链大面积显示「异常」

历史原因：检测器请求头声明了 `Accept-Encoding: gzip, deflate, br`，但运行环境没有安装 Brotli，
凡是返回 Brotli 压缩的站点都会抛 `ContentEncodingError` 并被判为不可访问。
现已改为 `gzip, deflate`。如果以后再出现，先看 Actions 日志里是否有
`Can not decode content-encoding: brotli`。

### 5.5 备用检测 API 失效

`conf.yaml` 里的 `https://v1.nsuuu.com/api/netCheck` 和 `/api/status` 目前返回 **502**，已经不可用。
它们只作为直连失败后的兜底，不影响正常检测；如果你想换掉，直接改 `backup_api_urls` 即可，
或者把 `use_backup_api` 设为 `false` 彻底关闭。
