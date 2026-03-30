先说结论：
**这个报错跟 Vercel 的 bug 无关，本质是：你这几个 commit（包括 3456ca5）在 Vercel 看来“没有合法的作者信息”，所以它拒绝用这个 commit 创建部署。**
最常见的原因就是：本地 `git` 没正确配置 `user.name / user.email`，或者 email 和你 GitHub 账号不匹配。

下面一步一步把坑填上。

---

## 1. 这个报错到底在说什么？

Vercel 有一条比较“严”的规则：

> 要部署某个 commit，必须能从 **commit 的 author 邮箱** 映射到一个有权限的 Vercel 账号。
> 如果找不到，就会报各种 author 相关错误，包括你看到的 **“A commit author is required”**。([Vercel][1])

社区里已经有人遇到一模一样的提示，最后发现都是 **git 提交没有设置 email 或 email 不对**：

* 官方 KB：如果本地 git 的 `user.email` 不等于你 GitHub 账号的邮箱，Vercel 没法验证这个 commit，部署就不会触发。([Vercel][1])
* 国人踩坑帖：报 `A commit author is required`，给本地仓库加上 `git config user.email "你的邮箱"` 后重新提交一次，Vercel 立刻恢复自动部署。([数字居民论坛][2])
* 另一个中文博客和 Vercel 社区帖也是同样结论：设置本地 `user.name`、`user.email` 为 GitHub 绑定的邮箱，再推一个新 commit，就不会再弹这个错误。([CSDN][3])

你现在在【Create Deployment】里填 `3456ca5`，Vercel 去查这个 commit 元数据，发现找不到合法 author，就直接在输入框下方报 `A commit author is required`。

---

## 2. 先检查一下这个 commit 的作者是不是“残缺”的

在 **你自己的 Mac 终端** 里，到 `totalchaos.info` 本地仓库执行：

```bash
cd /你本地的/totalchaos.info

# 看看最近一次提交
git log -1

# 或者专门看 3456ca5 这条
git log -1 3456ca5
```

重点看这一行：

```text
Author: XXX <YYY>
```

* `XXX`：作者名字
* `YYY`：作者邮箱

如果你看到的情况是：

* 邮箱为空，或者是乱七八糟的占位邮箱；
* 邮箱是另一个 Git 服务（比如 GitLab、公司邮箱），跟你现在这个 GitHub 账号无关；

那就印证了问题：**Vercel 找不到一个“能对应到你 GitHub / Vercel 账号的 email”**。

---

## 3. 正确配置本地 Git 作者信息

### 3.1 配置 user.name / user.email

在同一个终端里执行（建议至少在当前仓库配置，嫌麻烦可以直接全局 `--global`）：

```bash
# 仓库级别配置
git config user.name "libin257"
git config user.email "li15101042284@gmail.com
"
```

> ⚠️ 这里的邮箱**必须是**你 GitHub 账号绑定的邮箱之一（包括 `xxx+用户名@users.noreply.github.com` 这种也可以），否则 Vercel 还是认不出来。([Vercel][1])

可以再检查一下：

```bash
git config user.name
git config user.email
```

确认输出是你期望的值。

---

### 3.2 再推一个“干净的” commit

因为旧的那个 `3456ca5` 元数据已经不对了，我们只需要再来一个带正确 author 的 commit，让 Vercel 用新提交部署即可。

如果没有实际改动，可以做一个空提交：

```bash
git commit --allow-empty -m "chore: fix vercel commit author"
git push origin main
```

或者你刚好还要改代码，就正常改完再 `git add`、`git commit`、`git push` 即可。

> 这一招也是 StackOverflow / Vercel 社区里官方推荐的解决方式：用带明确 `--author` / 正确 email 的提交覆盖掉之前不规范的提交。([Stack Overflow][4])

---

## 4. 回到 Vercel 再试部署

现在你有了一个新的 commit（比如 hash 是 `abc1234`），接下来有两种方式：

### 方式 A：完全不用手动 Create Deployment

只要仓库已经通过【Vercel】绑定了：

1. 你刚才 `git push origin main` 完成后，
2. 打开【Vercel 项目 → Deployments】页面，
3. 理论上应该自动多出一条新的 Deployment（target 是 Production 或 Preview）。

如果有自动部署成功，其实就不用再点【Create Deployment】了。

### 方式 B：再试一次 “Create Deployment”

如果你就是想手动指定：

1. 打开【Vercel → 这个项目 → Deployments → 右上角 ⋯ → Create Deployment】。
2. 在 **Commit or Branch Reference** 里填：

   * 直接填 `main`（让它部署这个分支最新的 commit），**或者**
   * 填刚刚新 commit 的 hash（例如 `abc1234`）。
3. 这时候就不应该再出现 `A commit author is required` 了，而是可以正常走构建流程。

---

## 5. 还有可能的“隐藏雷点”（排查用）

大概率你按上面步骤做完就好了，但如果还出问题，可以顺手检查两件事（都是官方文档提到的）：([Vercel][5])

1. **确认这个 Vercel 项目所在账号 / Team，你是 Owner：**

   * 对 Hobby（免费）团队来说，私有仓库的 commit author 必须是这个 Hobby 团队的 owner，否则也会被拦。
2. **一个 GitHub 账号只能同时绑一个 Vercel 账号：**

   * 如果你之前还开过另一个 Vercel 账号也绑定了同一个 GitHub，可能会导致 “找不到 author”。
   * 需要在不用的那个 Vercel 账号里，去【Settings → Git】把 GitHub 解绑。

通常真正卡人的就是前面那一步：**git 提交里没有正确的 email**。你这边刚好也提到频繁在 VSCode / Cursor 等工具之间切换，很多人就是在切 IDE 时把 git 的 user.email 弄丢了，症状和你现在一模一样。([数字居民论坛][2])

搞定一次，后面所有新项目基本就不会再踩这个坑了。

[1]: https://vercel.com/kb/guide/why-aren-t-commits-triggering-deployments-on-vercel?utm_source=chatgpt.com "Why aren't commits triggering deployments on Vercel?"
[2]: https://shuzijumin.com/thread-3781-1-1.html?utm_source=chatgpt.com "遇到一个vercel 无法自动编译，并且手动创建部署也失败的问题"
[3]: https://blog.csdn.net/wzyleix97/article/details/142950306?utm_source=chatgpt.com "【Vercel】Vercel静态部署踩坑原创"
[4]: https://stackoverflow.com/questions/79011901/error-vercel-git-author-must-have-access-to-the-project-on-vercel-to-create-d?utm_source=chatgpt.com "Error: Vercel - Git author must have access to the project on ..."
[5]: https://vercel.com/docs/git?utm_source=chatgpt.com "Deploying Git Repositories with Vercel"
