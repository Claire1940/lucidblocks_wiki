# Vercel 本地验证与部署完整教程

## 为什么使用本地验证？

在推送代码到 Git 之前进行本地验证可以：
- 及早发现 `vercel.json` 配置错误
- 避免反复推送 Git 来修复配置问题
- 节省 CI/CD 资源和时间
- 在本地调试构建失败原因
- 直接部署验证过的构建产物

---

## 前置要求（已完成）

1. 安装 Vercel CLI：
```bash
npm install -g vercel
```

2. 登录 Vercel 账户：
```bash
vercel login
```
或使用 npx（无需全局安装）：
```bash
npx vercel login
```

---

## 完整部署流程

### 步骤 1：验证 vercel.json 语法

在开始之前，先验证配置文件的 JSON 语法：

```bash
node -e "JSON.parse(require('fs').readFileSync('vercel.json', 'utf8')); console.log('✓ vercel.json 语法正确')"
```

**预期输出：**
```
✓ vercel.json 语法正确
```

---

### 步骤 2：创建/链接 Vercel 项目

根据你的情况选择以下方式之一：

#### 方式 1：自动创建项目（推荐新项目）

如果你还没有 Vercel 项目，直接运行：

```bash
vercel
```

Vercel CLI 会**自动引导你创建新项目**：

```
? Set up and deploy "~/your-project"? [Y/n] y
? Which scope do you want to deploy to? Your Team
? Link to existing project? [y/N] n
? What's your project's name? your-project-name
? In which directory is your code located? ./
```

CLI 会自动：
- 创建 Vercel 项目
- 链接本地目录
- 执行初次部署

**完成后可跳过步骤 3，直接进入步骤 4**

---

#### 方式 2：链接到已有项目（推荐已有项目）

如果你已经在 Vercel 网站上创建了项目（如通过 Git 自动创建），使用：

```bash
vercel link --yes --project=你的项目名
```

或者让 Vercel 自动检测：
```bash
vercel link --yes
```

**预期输出：**
```
Linked to 你的团队/你的项目 (created .vercel)
Retrieving project...
> Downloading `development` Environment Variables
Updated .env.local file and added it to .gitignore
```

**生成的文件：**
- `.vercel/` 目录（包含项目配置）
- `.env.local`（环境变量，已自动添加到 .gitignore）

---

### 步骤 3：拉取项目设置与环境变量

强烈建议执行此步骤，让本地构建尽量贴近云端配置：

```bash
vercel pull --yes
```

**预期输出：**
```
> Downloading `development` Environment Variables
Created .vercel/.env.development.local file

> Downloading project settings
Downloaded project settings to .vercel/project.json
```

**作用：**
- 下载云端的环境变量
- 下载项目配置
- 确保本地构建与生产环境一致

---

### 步骤 4：本地构建（关键步骤）

这是验证配置的关键步骤，会在本地执行完整的生产构建：

```bash
vercel build --prod
```

**预期输出：**
```
Installing dependencies...
Detected Next.js version: 15.5.6
Running "npm run build"

   Creating an optimized production build ...
 ✓ Compiled successfully
   Linting and checking validity of types ...
 ✓ Generating static pages (46/46)

Build Completed in .vercel/output [23s]
```

**重要说明：**
- 构建产物输出到 `.vercel/output` 目录
- 如果这一步失败，说明配置有问题，需要修复后再试
- 这里会验证 `vercel.json` 中的所有配置
- 比直接推送 Git 更快发现问题

---

### 步骤 5：部署预构建产物

将本地构建的产物直接上传到 Vercel，无需推送 Git：

```bash
vercel deploy --prebuilt --prod
```

**参数说明：**
- `--prebuilt`：使用上一步的 `.vercel/output` 构建产物
- `--prod`：部署到生产环境（而非预览环境）

**预期输出：**
```
Uploading [====================] (5.9MB/5.9MB)
Inspect: https://vercel.com/你的团队/你的项目/部署ID
Production: https://你的域名.vercel.app
Building: Using prebuilt build artifacts from .vercel/output
Building: Deployment completed

Production: https://你的域名.vercel.app [33s]
```

---

## 常用命令

### 查看部署日志
```bash
vercel inspect 部署URL --logs
```

### 查看最新部署
```bash
vercel ls
```

### 重新部署
```bash
vercel redeploy 部署URL
```

### 仅部署预览（非生产）
```bash
vercel deploy --prebuilt
```

### 查看项目信息
```bash
vercel project ls
```

---

## 常见问题与解决方案

### 1. 项目名称错误

**错误信息：**
```
Error: Project names can be up to 100 characters long and must be lowercase...
```

**解决方案：**
- 使用 `--project=项目名` 明确指定项目名称
- 确保项目名称只包含小写字母、数字、`.`、`_`、`-`
- 不能包含 `---` 序列

### 2. 未登录 Vercel

**错误信息：**
```
Error: Not authenticated
```

**解决方案：**
```bash
vercel login
```

### 3. 构建失败

**排查步骤：**
1. 先在本地运行 `npm run build` 确保基础构建通过
2. 检查 `vercel.json` 配置是否正确
3. 查看构建日志找到具体错误
4. 确保环境变量已正确配置

### 4. 文件上传限制

如果项目文件过多或过大：

```bash
vercel deploy --prebuilt --prod --archive=tgz
```

使用压缩参数减少上传负担。

---

## vercel.json 配置示例

### 基础 Next.js 配置
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs"
}
```

### 带重定向规则
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "redirects": [
    {
      "source": "/old-path",
      "destination": "/new-path",
      "permanent": true
    }
  ]
}
```

### 带环境变量
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.example.com"
  }
}
```

---

## 最佳实践

### 1. 推送前验证
```bash
# 每次推送前运行这个流程
node -e "JSON.parse(require('fs').readFileSync('vercel.json', 'utf8'))" && \
npm run build && \
echo "✓ 验证通过，可以安全推送"
```

### 2. 使用 .vercelignore
创建 `.vercelignore` 文件排除不必要的文件：
```
# .vercelignore
node_modules
.git
*.log
.DS_Store
.vscode
```

### 3. 本地测试环境变量
```bash
# 使用本地环境变量运行构建
vercel build --prod
```

### 4. 自动化脚本
在 `package.json` 添加快捷命令：
```json
{
  "scripts": {
    "vercel:build": "vercel build --prod",
    "vercel:deploy": "vercel deploy --prebuilt --prod",
    "vercel:validate": "node -e \"JSON.parse(require('fs').readFileSync('vercel.json', 'utf8'))\" && npm run build"
  }
}
```

使用：
```bash
npm run vercel:validate  # 验证配置和构建
npm run vercel:build     # 本地构建
npm run vercel:deploy    # 部署
```

---

## 完整工作流程图

```
┌─────────────────────────────────────┐
│ 1. 验证 vercel.json 语法            │
│    node -e "JSON.parse(...)"        │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ 2. 链接 Vercel 项目（首次）         │
│    vercel link --yes                │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ 3. 拉取项目设置                     │
│    vercel pull --yes                │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ 4. 本地构建验证                     │
│    vercel build --prod              │
│    产物 → .vercel/output            │
└──────────────┬──────────────────────┘
               │
               ├─→ 构建失败？
               │   └─→ 修复问题，返回步骤1
               │
               ↓ 构建成功
┌─────────────────────────────────────┐
│ 5. 部署构建产物                     │
│    vercel deploy --prebuilt --prod  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ ✓ 部署成功                          │
│   访问生产环境 URL                  │
└─────────────────────────────────────┘
```

---

## 对比：传统 Git 部署 vs 本地验证部署

| 特性 | Git 自动部署 | 本地验证部署 |
|------|-------------|--------------|
| **配置验证时机** | 推送后 | 推送前 |
| **发现错误速度** | 慢（需等待 CI） | 快（本地立即发现） |
| **Git 提交次数** | 多（反复修复） | 少（一次成功） |
| **CI/CD 资源消耗** | 高 | 低 |
| **调试便利性** | 难（远程日志） | 易（本地完整日志） |
| **适用场景** | 配置稳定时 | 配置调试时 |

---

## 总结

使用 Vercel CLI 本地验证部署流程：

1. ✅ 提前发现配置问题
2. ✅ 减少 Git 提交历史污染
3. ✅ 节省时间和资源
4. ✅ 提高部署成功率
5. ✅ 更好的调试体验

**推荐工作流：**
- 开发时：使用 Git 自动部署
- 配置变更时：使用本地验证部署
- 重要更新时：使用本地验证部署

---

## 参考链接

- [Vercel CLI 官方文档](https://vercel.com/docs/cli)
- [Build Output API](https://vercel.com/docs/build-output-api/v3)
- [vercel.json 配置参考](https://vercel.com/docs/projects/project-configuration)
- [环境变量配置](https://vercel.com/docs/projects/environment-variables)
