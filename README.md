# 小米钱包每日任务多平台应用

[![GitHub Actions Status](https://github.com/kai648846760/xiaomiwallet/actions/workflows/daily-checkin.yml/badge.svg)](https://github.com/kai648846760/xiaomiwallet/actions/workflows/daily-checkin.yml)
[![Build Status](https://github.com/kai648846760/xiaomiwallet/actions/workflows/build-app.yml/badge.svg)](https://github.com/kai648846760/xiaomiwallet/actions/workflows/build-app.yml)

## 🚨 **<span style="color:red">重要警告</span>** 🚨

### **<span style="color:red; font-weight:bold">⚠️ 服务器运行风险极高，强烈建议使用GUI本地模式！</span>**

**<span style="color:red; font-weight:bold">使用GitHub Actions或其他服务器自动化方式运行此程序有很大概率导致小米账号异常或被封禁！</span>**

**推荐使用方式：**
- ✅ **GUI本地运行**：下载桌面版或移动版应用，在本地设备上运行
- ✅ **降低封号风险**：本地IP环境更安全，避免服务器IP被识别为异常
- ✅ **完全可控**：可以随时停止、调整执行频率和时间

**<span style="color:red; font-weight:bold">如果您仍要使用服务器自动化模式，请自行承担账号风险！</span>**

---

基于Flet框架开发的跨平台小米钱包每日任务应用，支持以下平台：

📱 **移动端**: Android APK、iOS IPA
💻 **桌面端**: Windows、macOS
☁️ **云端**: GitHub Actions自动化

**Windows平台编码问题已修复**：现在Windows用户可以正常使用所有功能，包括中文字符显示和文件操作。

无论你喜欢哪种方式，都能轻松实现小米钱包每日任务的自动化管理。

## 📥 应用下载与使用

### 📱 移动端下载

从 [Releases页面](https://github.com/kai648846760/xiaomiwallet/releases) 下载移动端版本：

- **Android**: `xiaomi-wallet-gui-android.zip` - 解压后安装 `.apk` 文件
- **iOS**: `xiaomi-wallet-gui-ios.zip` - 解压后通过Xcode或TestFlight安装 `.ipa` 文件

### 💻 桌面端下载

从 [Releases页面](https://github.com/kai648846760/xiaomiwallet/releases) 下载桌面端版本：

- **Windows**: `xiaomi-wallet-gui-windows.zip` - 解压后运行可执行文件
- **macOS**: `xiaomi-wallet-gui-macos.tar.gz` - 解压后运行 `.app` 文件

### 🚀 使用步骤

1. **选择平台**：根据您的设备选择对应版本下载
2. **安装应用**：
   - 移动端：安装APK/IPA文件
   - 桌面端：解压后直接运行
   - Web端：部署到服务器或本地运行
3. **添加账号**：点击"添加账号"按钮，扫描二维码登录
4. **执行任务**：选择账号后点击"执行任务"开始自动签到
5. **查看结果**：在界面中查看任务执行结果和历史记录

### 🛠️ 从源码运行

如果你想从源码运行或进行开发：

```bash
# 克隆项目
git clone https://github.com/kai648846760/xiaomiwallet.git
cd xiaomiwallet

# 安装依赖
pip install flet requests qrcode urllib3
# 或使用 uv: uv sync

# 运行应用（自动在浏览器中打开）
flet run gui.py

# 或者运行Web版本
flet run gui.py --web
```

## 🌟 项目特色

### 🚀 多平台支持

* **📱 移动端原生体验**：Android APK和iOS IPA，随时随地管理任务
* **💻 桌面端完整功能**：Windows、macOS桌面应用，已修复Windows编码问题
* **☁️ 云端自动化**：GitHub Actions无服务器自动执行

### 🎯 核心功能

* **🎨 统一用户界面**：基于Flet框架的跨平台一致性体验
* **👥 多账号管理**：可视化添加、删除和管理多个小米账号
* **📱 扫码登录**：内置二维码生成，手机扫码即可完成账号添加
* **⚡ 实时执行**：一键执行所有账号任务，实时显示执行进度
* **📊 结果查看**：详细的任务执行记录和结果展示
* **🔄 自动刷新**：执行记录按时间倒序显示，最新结果一目了然
* **💾 数据同步**：跨平台配置文件同步

### 🔧 技术优势

* **🏗️ 现代架构**：基于Flet框架，Python后端 + Flutter前端
* **📦 一键构建**：支持所有平台的自动化构建和发布
* **🔐 安全可靠**：账号凭证通过 GitHub Repository Secrets 加密存储，代码中不涉及任何明文密钥，安全透明
* **🕒 自动执行**：每日定时自动运行，一次配置，长期有效
* **🔔 飞书消息推送 (可选)**：支持将每日运行结果通过飞书自定义机器人推送到指定会话
* **🍴 "开箱即用"**：目标是让任何用户 Fork 本仓库后，都能通过本说明文档快速配置并成功运行
* **🌍 全球部署**：利用GitHub的全球基础设施

## ⚙️ 工作原理

1. **本地获取凭证**：用户在自己的电脑上运行 `login.py` 脚本，通过扫码生成包含安全凭证的 `xiaomiconfig.json` 文件。
2. **云端安全存储**：用户将 `xiaomiconfig.json` 文件的**内容**复制并存储到自己仓库的 `GitHub Secrets` 中。
3. **定时自动触发**：GitHub Actions 根据预设的 `cron` 表达式，每日定时唤醒。
4. **动态执行任务**：工作流（Workflow）启动一个虚拟机，检出项目代码，从 `Secrets` 中读取凭证内容并动态生成配置文件，最后执行 `main.py` 脚本完成所有任务。
5. **发送通知 (可选)**：如果配置了飞书 Webhook，脚本会将任务结果推送到飞书。

## 🚀 快速开始：三步让你的项目跑起来

请严格按照以下步骤操作，即可完成所有配置。

### 步骤一：Fork 本项目到你的仓库

点击本项目页面右上角的 **Fork** 按钮，将项目复制一份到你自己的 GitHub 账号下。后续所有操作都在你 Fork 后的仓库中进行。

### 步骤二：在本地生成你的账号配置文件

这一步的目的是安全地生成包含你账号凭证的 `xiaomiconfig.json` 文件。**此过程在你的电脑上完成，不会上传任何敏感文件。**

1. **克隆你 Fork 后的项目到本地**：

   ```bash
   git clone https://github.com/kai648846760/xiaomiwallet.git
   cd xiaomiwallet
   ```
2. **安装依赖**：
   推荐使用 `uv` 或 `pip` 安装项目所需的 Python 包。

   ```bash
   # 安装依赖 (三选一即可)
   pip install requests qrcode urllib3
   # 或者 pip3 install requests qrcode urllib3
   # 如果你有 uv，可以直接 uv sync
   ```
3. **运行登录脚本生成配置**：
   执行 `login.py` 脚本，并为你自己的账号起一个**英文别名**（例如 `my_account1`）。

   ```bash
   python3 login.py my_account1
   ```

   * 此时，终端会显示一个**二维码**。
   * 请打开你手机上的**小米社区**或**小米商城** App（**不是小米钱包！**），使用其中的“扫一扫”功能扫描终端的二维码。
   * 在手机上点击“确认登录”。
   * 脚本会自动捕获登录凭证，并生成一个名为 `xiaomiconfig.json` 的文件。
4. **（可选）添加更多账号**：
   如果你有多个账号，重复第 3 步即可，每次使用**不同的别名**。例如：

   ```bash
   python3 login.py my_account2
   ```

   新的账号信息会自动追加到 `xiaomiconfig.json` 文件中。
5. **复制配置文件内容**：
   **打开**你项目目录下的 `xiaomiconfig.json` 文件，**全选并复制**里面的所有文本内容。

### 步骤三：在 GitHub 仓库中配置 Secret 和 Actions

这一步是将你的账号凭证安全地配置到你 Fork 后的仓库中。

1. **进入你 Fork 后的 GitHub 仓库页面**。
2. 点击仓库顶部的 **Settings** -> 左侧菜单 **Secrets and variables** -> **Actions**。
3. 点击右上角的 **New repository secret** 按钮。
4. **创建 Secret**：

   * **Name**: 必须、必须、必须填写 `XIAOMI_CONFIG_JSON` (请直接复制，确保完全一致)。
   * **Secret**: 将你在【步骤二】中复制的 `xiaomiconfig.json` 的**完整内容**粘贴到这里。
   * 点击 **Add secret** 按钮保存。
5. **启用并测试 Actions**：

   * 点击仓库顶部的 **Actions** 标签页。
   * 你可能会看到一个提示：“Workflows aren't running on this forked repository”。点击黄色的 **I understand my workflows, go ahead and enable them** 按钮来启用 Actions。
   * 在左侧列表中，点击 **小米钱包每日任务** 这个工作流。
   * 在右侧，你会看到一个 “This workflow has a `workflow_dispatch` event trigger.” 的提示，旁边有一个 **Run workflow** 的下拉按钮。
   * 点击 **Run workflow** 按钮，可以立即手动触发一次任务，用来测试你的配置是否正确。

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

* **Q: 任务执行失败，日志里出现 `401 Unauthorized` 错误怎么办？**

  * **A:** 这是最常见的问题，意味着你的账号登录凭证 (`passToken`) 已过期。**解决方案**：只需在本地重新执行一次【步骤二】中的 `python3 login.py <你的别名>`，获取新的 `xiaomiconfig.json` 内容，然后更新到 GitHub 的 `XIAOMI_CONFIG_JSON` Secret 中即可。
* **Q: 我可以修改每日任务的执行时间吗？**

  * **A:** 当然。请编辑项目中的 `.github/workflows/daily-checkin.yml` 文件，找到 `cron: '30 2 * * *'` 这一行。这是一个标准的 `cron` 表达式，但请注意**这里的时间是 UTC 时间**。你需要换算成你所在时区的时间（UTC+8 = 北京时间）。例如，`'0 1 * * *'` 对应北京时间上午 9:00。
* **Q: 项目是安全的吗？我的账号信息会泄露吗？**

  * **A:** 本项目是完全安全的。你的账号凭证仅存储在你自己的 GitHub 仓库的加密 `Secrets` 中，除了你本人和 GitHub Actions 的虚拟机，没有任何人可以访问到。代码完全开源，你可以审查每一行。

## 🔨 开发者信息

### 🏗️ 多平台自动构建系统

本项目使用GitHub Actions + Flet构建系统，支持多平台的自动化构建：

- **🚀 自动触发**：推送标签时自动构建所有平台版本
- **🎯 手动触发**：在Actions页面手动触发构建
- **📱 支持平台**：Windows、macOS、Android、iOS（已修复Windows编码问题）
- **🛠️ 构建工具**：Flet + Flutter SDK + 平台特定工具链

### 📦 构建架构

- **桌面端**：使用Flet构建原生应用（Windows、macOS）
- **移动端**：生成APK和IPA文件（Android、iOS）
- **依赖管理**：基于pyproject.toml的现代Python项目结构

### 🚀 发布新版本

要发布新版本，请按以下步骤操作：

```bash
# 1. 更新版本号（在pyproject.toml中）
# 2. 提交更改
git add .
git commit -m "Release v1.0.0"

# 3. 创建并推送标签
git tag v1.0.0
git push origin v1.0.0

# 4. GitHub Actions会自动构建所有平台并创建Release
```

### 🛠️ 本地构建

#### 安装构建环境

```bash
# 安装Flet和依赖
pip install flet requests qrcode urllib3

# 安装Flutter SDK（构建移动端需要）
# 参考：https://flutter.dev/docs/get-started/install
```

#### 构建不同平台

```bash
# 构建桌面应用
flet build windows    # Windows（已修复编码问题）
flet build macos      # macOS

# 构建移动应用
flet build apk        # Android APK
flet build aab        # Android App Bundle
flet build ipa        # iOS (需要macOS)

# 构建结果在 build/ 目录
```

## 📜 免责声明

本项目仅用于个人学习和技术研究，请在遵守相关法律法规的前提下使用。

由于小米官方接口可能随时发生变化，本项目不保证其功能的长期可用性。

用户在使用本项目时，应自行承担因使用不当或项目失效等原因可能造成的任何风险和损失。