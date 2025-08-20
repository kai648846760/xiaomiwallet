# 小米钱包每日任务 - GitHub Actions 全自动版

[![GitHub Actions Status](https://github.com/kai648846760/xiaomiwallet/actions/workflows/daily-checkin.yml/badge.svg)](https://github.com/kai648846760/xiaomiwallet/actions/workflows/daily-checkin.yml)

这是一个部署在 GitHub Actions 上的全自动、无服务器（Serverless）小米钱包每日任务工具。

你不需要自己的服务器，也不需要复杂的环境配置。**只需 Fork 本项目，通过几个简单的步骤配置一下你的账号信息，即可实现每日自动执行任务，彻底解放双手。**

## ✨ 项目特色

*   **🚀 Serverless**：完全基于免费的 GitHub Actions 运行，无需任何服务器成本。
*   **🕒 自动执行**：每日定时自动运行，一次配置，长期有效。
*   **🔐 安全可靠**：账号凭证通过 GitHub Repository Secrets 加密存储，代码中不涉及任何明文密钥，安全透明。
*   **📱 终端二维码登录**：在本地通过命令行生成二维码，手机 App 扫码即可完成登录，过程安全便捷。
*   **👥 多账号支持**：支持通过配置文件管理多个小米账号。
*   **🔔 飞书消息推送 (可选)**：支持将每日运行结果通过飞书自定义机器人推送到指定会话。
*   **🍴 “开箱即用”**：目标是让任何用户 Fork 本仓库后，都能通过本说明文档快速配置并成功运行。

## ⚙️ 工作原理

1.  **本地获取凭证**：用户在自己的电脑上运行 `login.py` 脚本，通过扫码生成包含安全凭证的 `xiaomiconfig.json` 文件。
2.  **云端安全存储**：用户将 `xiaomiconfig.json` 文件的**内容**复制并存储到自己仓库的 `GitHub Secrets` 中。
3.  **定时自动触发**：GitHub Actions 根据预设的 `cron` 表达式，每日定时唤醒。
4.  **动态执行任务**：工作流（Workflow）启动一个虚拟机，检出项目代码，从 `Secrets` 中读取凭证内容并动态生成配置文件，最后执行 `xiaomi.py` 脚本完成所有任务。
5.  **发送通知 (可选)**：如果配置了飞书 Webhook，脚本会将任务结果推送到飞书。

## 🚀 快速开始：三步让你的项目跑起来

请严格按照以下步骤操作，即可完成所有配置。

### 步骤一：Fork 本项目到你的仓库

点击本项目页面右上角的 **Fork** 按钮，将项目复制一份到你自己的 GitHub 账号下。后续所有操作都在你 Fork 后的仓库中进行。

### 步骤二：在本地生成你的账号配置文件

这一步的目的是安全地生成包含你账号凭证的 `xiaomiconfig.json` 文件。**此过程在你的电脑上完成，不会上传任何敏感文件。**

1.  **克隆你 Fork 后的项目到本地**：
    ```bash
    git clone https://github.com/kai648846760/xiaomiwallet.git
    cd xiaomiwallet
    ```

2.  **安装依赖**：
    推荐使用 `uv` 或 `pip` 安装项目所需的 Python 包。
    ```bash
    # 安装依赖 (三选一即可)
    pip install requests qrcode urllib3
    # 或者 pip3 install requests qrcode urllib3
    # 如果你有 uv，可以直接 uv sync
    ```

3.  **运行登录脚本生成配置**：
    执行 `login.py` 脚本，并为你自己的账号起一个**英文别名**（例如 `my_account1`）。
    ```bash
    python3 login.py my_account1
    ```
    *   此时，终端会显示一个**二维码**。
    *   请打开你手机上的**小米社区**或**小米商城** App（**不是小米钱包！**），使用其中的“扫一扫”功能扫描终端的二维码。
    *   在手机上点击“确认登录”。
    *   脚本会自动捕获登录凭证，并生成一个名为 `xiaomiconfig.json` 的文件。

4.  **（可选）添加更多账号**：
    如果你有多个账号，重复第 3 步即可，每次使用**不同的别名**。例如：
    ```bash
    python3 login.py my_account2
    ```
    新的账号信息会自动追加到 `xiaomiconfig.json` 文件中。

5.  **复制配置文件内容**：
    **打开**你项目目录下的 `xiaomiconfig.json` 文件，**全选并复制**里面的所有文本内容。

### 步骤三：在 GitHub 仓库中配置 Secret 和 Actions

这一步是将你的账号凭证安全地配置到你 Fork 后的仓库中。

1.  **进入你 Fork 后的 GitHub 仓库页面**。

2.  点击仓库顶部的 **Settings** -> 左侧菜单 **Secrets and variables** -> **Actions**。

3.  点击右上角的 **New repository secret** 按钮。

4.  **创建 Secret**：
    *   **Name**: 必须、必须、必须填写 `XIAOMI_CONFIG_JSON` (请直接复制，确保完全一致)。
    *   **Secret**: 将你在【步骤二】中复制的 `xiaomiconfig.json` 的**完整内容**粘贴到这里。
    *   点击 **Add secret** 按钮保存。

5.  **启用并测试 Actions**：
    *   点击仓库顶部的 **Actions** 标签页。
    *   你可能会看到一个提示：“Workflows aren't running on this forked repository”。点击黄色的 **I understand my workflows, go ahead and enable them** 按钮来启用 Actions。
    *   在左侧列表中，点击 **小米钱包每日任务** 这个工作流。
    *   在右侧，你会看到一个 “This workflow has a `workflow_dispatch` event trigger.” 的提示，旁边有一个 **Run workflow** 的下拉按钮。
    *   点击 **Run workflow** 按钮，可以立即手动触发一次任务，用来测试你的配置是否正确。

**🎉 恭喜！所有配置均已完成！**

从现在起，GitHub Actions 将在北京时间每日上午 10:30 左右自动为你执行签到任务。你可以在 Actions 标签页查看每一次的运行日志。

## 🔧 配置文件格式与飞书推送 (可选)

你可以通过手动编辑 `xiaomiconfig.json` 的内容（并更新到 GitHub Secret 中）来配置飞书推送。

在 `data` 字段内，为你需要推送的账号添加一个 `"feishu_webhook"` 字段即可。

**基础配置 (无推送):**
```json
[
    {
        "data": {
            "us": "my_account1",
            "userId": "123456789",
            "passToken": "...",
            "securityToken": "...",
            "log": null
        }
    }
]
```

**高级配置 (带飞书推送):**
```json
[
    {
        "data": {
            "us": "my_account1",
            "userId": "123456789",
            "passToken": "...",
            "securityToken": "...",
            "log": null,
            "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/你的机器人KEY"
        }
    }
]
```

## ❓ 常见问题 (FAQ)

*   **Q: 任务执行失败，日志里出现 `401 Unauthorized` 错误怎么办？**
    *   **A:** 这是最常见的问题，意味着你的账号登录凭证 (`passToken`) 已过期。**解决方案**：只需在本地重新执行一次【步骤二】中的 `python3 login.py <你的别名>`，获取新的 `xiaomiconfig.json` 内容，然后更新到 GitHub 的 `XIAOMI_CONFIG_JSON` Secret 中即可。

*   **Q: 我可以修改每日任务的执行时间吗？**
    *   **A:** 当然。请编辑项目中的 `.github/workflows/daily-checkin.yml` 文件，找到 `cron: '30 2 * * *'` 这一行。这是一个标准的 `cron` 表达式，但请注意**这里的时间是 UTC 时间**。你需要换算成你所在时区的时间（UTC+8 = 北京时间）。例如，`'0 1 * * *'` 对应北京时间上午 9:00。

*   **Q: 项目是安全的吗？我的账号信息会泄露吗？**
    *   **A:** 本项目是完全安全的。你的账号凭证仅存储在你自己的 GitHub 仓库的加密 `Secrets` 中，除了你本人和 GitHub Actions 的虚拟机，没有任何人可以访问到。代码完全开源，你可以审查每一行。

## 📜 免责声明

本项目仅用于个人学习和技术研究，请在遵守相关法律法规的前提下使用。

由于小米官方接口可能随时发生变化，本项目不保证其功能的长期可用性。

用户在使用本项目时，应自行承担因使用不当或项目失效等原因可能造成的任何风险和损失。