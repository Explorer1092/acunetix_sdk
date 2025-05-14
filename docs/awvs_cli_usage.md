# Acunetix AWVS CLI (`main_cli.py`) 用法指南

`main_cli.py` 是一个命令行工具，用于通过 Acunetix API 与您的 Acunetix AWVS (Acunetix Web Vulnerability Scanner) 实例进行交互。它允许您管理扫描目标、启动和管理扫描任务以及检索扫描结果。

## 目录
- [Acunetix AWVS CLI (`main_cli.py`) 用法指南](#acunetix-awvs-cli-main_clipy-用法指南)
  - [目录](#目录)
  - [1. 先决条件](#1-先决条件)
  - [2. 配置凭据](#2-配置凭据)
    - [使用 `login` 命令 (推荐)](#使用-login-命令-推荐)
    - [使用环境变量](#使用环境变量)
    - [配置加载顺序](#配置加载顺序)
    - [配置文件位置和安全](#配置文件位置和安全)
  - [3. 通用用法](#3-通用用法)
  - [4. 模块和操作](#4-模块和操作)
    - [登录配置 (`login`)](#登录配置-login)
    - [目标管理 (`targets`)](#目标管理-targets)
      - [列出目标 (`list`)](#列出目标-list)
      - [添加目标 (`add`)](#添加目标-add)
      - [删除目标 (`delete`)](#删除目标-delete)
    - [扫描管理 (`scans`)](#扫描管理-scans)
      - [启动扫描 (`start`)](#启动扫描-start)
      - [列出扫描 (`list`)](#列出扫描-list)
      - [获取扫描状态 (`status`)](#获取扫描状态-status)
      - [获取扫描结果 (`results`)](#获取扫描结果-results)
      - [中止扫描 (`stop`)](#中止扫描-stop)
      - [删除扫描 (`delete`)](#删除扫描-delete)
    - [扫描配置管理 (`scan_profiles`)](#扫描配置管理-scan_profiles)
      - [列出扫描配置 (`list`)](#列出扫描配置-list)
      - [获取扫描配置详情 (`get`)](#获取扫描配置详情-get)
    - [目标组管理 (`target_groups`)](#目标组管理-target_groups)
      - [列出目标组 (`list`)](#列出目标组-list)
      - [创建目标组 (`create`)](#创建目标组-create)
      - [获取目标组详情 (`get`)](#获取目标组详情-get)
      - [更新目标组 (`update`)](#更新目标组-update)
      - [删除目标组 (`delete`)](#删除目标组-delete)
    - [报告管理 (`reports`)](#报告管理-reports)
      - [列出报告 (`list`)](#列出报告-list)
      - [生成报告 (`generate`)](#生成报告-generate)
      - [获取报告详情 (`get`)](#获取报告详情-get)
      - [删除报告 (`delete`)](#删除报告-delete)
    - [报告模板 (`report_templates`)](#报告模板-report_templates)
      - [列出模板 (`list`)](#列出模板-list)
      - [获取模板详情 (`get`)](#获取模板详情-get)
    - [用户管理 (`users`)](#用户管理-users)
      - [列出用户 (`list`)](#列出用户-list)
      - [创建用户 (`create`)](#创建用户-create)
      - [获取用户详情 (`get`)](#获取用户详情-get)
      - [更新用户 (`update`)](#更新用户-update)
      - [删除用户 (`delete`)](#删除用户-delete)
    - [用户组管理 (`user_groups`)](#用户组管理-user_groups)
      - [列出用户组 (`list`)](#列出用户组-list)
      - [创建用户组 (`create`)](#创建用户组-create)
    - [角色管理 (`roles`)](#角色管理-roles)
      - [列出角色 (`list`)](#列出角色-list)
      - [创建角色 (`create`)](#创建角色-create)
    - [漏洞管理 (`vulnerabilities`)](#漏洞管理-vulnerabilities)
      - [列出漏洞 (`list`)](#列出漏洞-list)
      - [获取漏洞详情 (`get`)](#获取漏洞详情-get)
      - [更新漏洞状态 (`update_status`)](#更新漏洞状态-update_status)
    - [导出任务 (`exports`)](#导出任务-exports)
      - [列出导出类型 (`list_types`)](#列出导出类型-list_types)
      - [创建导出 (`create`)](#创建导出-create)
    - [通知配置 (`notifications`)](#通知配置-notifications)
      - [列出通知 (`list`)](#列出通知-list)
      - [创建通知 (`create`)](#创建通知-create)
    - [问题跟踪器 (`issue_trackers`)](#问题跟踪器-issue_trackers)
      - [列出跟踪器 (`list`)](#列出跟踪器-list)
      - [创建跟踪器 (`create`)](#创建跟踪器-create)
    - [WAF 集成 (`wafs`)](#waf-集成-wafs)
      - [列出 WAF (`list`)](#列出-waf-list)
      - [创建 WAF (`create`)](#创建-waf-create)
    - [排除时段 (`excluded_hours`)](#排除时段-excluded_hours)
      - [列出排除时段 (`list`)](#列出排除时段-list)
      - [创建排除时段 (`create`)](#创建排除时段-create)
    - [代理配置 (`agents_config`)](#代理配置-agents_config)
      - [获取代理配置 (`get`)](#获取代理配置-get)
      - [获取注册令牌 (`get_token`)](#获取注册令牌-get_token)
    - [扫描代理 (`workers`)](#扫描代理-workers)
      - [列出扫描代理 (`list`)](#列出扫描代理-list)
      - [授权扫描代理 (`authorize`)](#授权扫描代理-authorize)
  - [5. 示例](#5-示例)
  - [6. 调试](#6-调试)

## 1. 先决条件

*   Python 3.x
*   已安装 `acunetix_sdk` 包 (通常此脚本位于 SDK 的 `examples/cli` 目录中，因此 SDK 应已可用)
*   可以访问您的 Acunetix AWVS 实例 API。

## 2. 配置凭据

您可以通过以下任一方式配置 `main_cli.py` 连接到 Acunetix API 所需的凭据：

### 使用 `login` 命令 (推荐)
这是推荐的配置方式，它会将您的 API URL 和 API Key 保存到一个本地配置文件中，供后续命令使用。

**用法:**
```bash
python examples/cli/main_cli.py login --api_url <API_URL> --api_key <API_KEY>
```
*   `<API_URL>`: 您的 Acunetix API 的完整 URL (例如, `https://your-acunetix-instance.com`)。
*   `<API_KEY>`: 您的 Acunetix API 密钥。

如果不提供参数，系统将提示您输入这些值。执行此命令后，凭据将保存在配置文件中。

### 使用环境变量
如果您不想使用配置文件，或者想临时覆盖配置文件中的设置，可以设置以下环境变量：

*   `AWVS_API_URL`: 您的 Acunetix API 的完整 URL。
*   `AWVS_API_KEY`: 您的 Acunetix API 密钥。

**示例 (bash):**
```bash
export AWVS_API_URL="https://your-acunetix-instance.com"
export AWVS_API_KEY="your_api_key_here"
# 然后运行脚本
python examples/cli/main_cli.py targets list
```

### 配置加载顺序
脚本将按以下顺序查找配置：
1.  **配置文件**: 如果存在且包含有效的 URL 和 Key。
2.  **环境变量**: 如果配置文件未找到或不完整，则尝试从 `AWVS_API_URL` 和 `AWVS_API_KEY` 环境变量加载。

如果两种方式都无法获取有效的配置，脚本将报错并退出。

### 配置文件位置和安全
*   **位置**: 配置文件默认存储在用户主目录下的 `~/.config/awvs_cli/config.json`。
*   **安全**: 请注意，API 密钥以明文形式存储在配置文件中。请确保此文件的权限得到妥善管理 (脚本会尝试将其设置为 `600`，即仅用户可读写)，并避免在不安全的环境中共享此文件。

## 3. 通用用法

脚本的基本调用结构如下：

```bash
python examples/cli/main_cli.py [模块] [操作] [参数...] [--debug]
```

您可以使用 `--help` 选项查看通用帮助信息或特定模块/操作的帮助：

```bash
python examples/cli/main_cli.py --help
python examples/cli/main_cli.py login --help
python examples/cli/main_cli.py targets --help
python examples/cli/main_cli.py targets add --help
```

## 4. 模块和操作

### 登录配置 (`login`)
保存 Acunetix API URL 和 API Key 到本地配置文件，以便后续命令使用，无需每次都设置环境变量。

**用法:**
```bash
python examples/cli/main_cli.py login --api_url <API_URL> --api_key <API_KEY>
```
*   `--api_url <API_URL>` (可选): 您的 Acunetix API 的完整 URL (例如 `https://acunetix.example.com`)。如果不提供，将提示输入。
*   `--api_key <API_KEY>` (可选): 您的 Acunetix API 密钥。如果不提供，将提示输入。

执行后，凭据将保存到 `~/.config/awvs_cli/config.json`。

---

### 目标管理 (`targets`)

此模块用于管理扫描目标。

#### 列出目标 (`list`)
列出所有已配置的目标。

**用法:**
```bash
python examples/cli/main_cli.py targets list [--limit <数量>]
```
*   `--limit <数量>` (可选): 限制返回的目标数量。默认为 100。

#### 添加目标 (`add`)
添加一个新的扫描目标。

**用法:**
```bash
python examples/cli/main_cli.py targets add <地址> <描述> [--criticality <重要性>]
```
*   `<地址>` (必需): 目标地址 (例如 `http://example.com`, `https://test.com`)。
*   `<描述>` (必需): 目标的描述性文本。
*   `--criticality <重要性>` (可选): 目标的重要性级别，范围从 0 到 100，必须是 10 的倍数 (例如 10, 20, ..., 100)。默认为 10。

#### 删除目标 (`delete`)
根据目标 ID 删除一个目标。

**用法:**
```bash
python examples/cli/main_cli.py targets delete <目标ID>
```
*   `<目标ID>` (必需): 要删除的目标的唯一标识符。

---

### 扫描管理 (`scans`)

此模块用于管理扫描任务。

#### 启动扫描 (`start`)
针对指定的目标启动一个新的扫描任务。

**用法:**
```bash
python examples/cli/main_cli.py scans start <目标ID> <扫描配置ID>
```
*   `<目标ID>` (必需): 要扫描的目标的唯一标识符。
*   `<扫描配置ID>` (必需): 用于扫描的扫描配置文件的唯一标识符。

CLI 会验证目标 ID 和扫描配置 ID 是否有效，然后启动扫描任务。

#### 列出扫描 (`list`)
列出所有扫描任务。

**用法:**
```bash
python examples/cli/main_cli.py scans list [--limit <数量>]
```
*   `--limit <数量>` (可选): 限制返回的扫描任务数量。默认为 20。

#### 获取扫描状态 (`status`)
获取特定扫描任务的当前状态和进度。

**用法:**
```bash
python examples/cli/main_cli.py scans status <扫描ID>
```
*   `<扫描ID>` (必需): 要查询状态的扫描任务的唯一标识符。

#### 获取扫描结果 (`results`)
获取特定扫描任务发现的漏洞列表。

**用法:**
```bash
python examples/cli/main_cli.py scans results <扫描ID> [--limit <数量>]
```
*   `<扫描ID>` (必需): 要获取结果的扫描任务的唯一标识符。
*   `--limit <数量>` (可选): 限制返回的漏洞数量。默认为 100。

#### 中止扫描 (`stop`)
中止一个正在进行的扫描任务。

**用法:**
```bash
python examples/cli/main_cli.py scans stop <扫描ID>
```
*   `<扫描ID>` (必需): 要中止的扫描任务的唯一标识符。

#### 删除扫描 (`delete`)
删除一个扫描任务的记录。

**用法:**
```bash
python examples/cli/main_cli.py scans delete <扫描ID>
```
*   `<扫描ID>` (必需): 要删除的扫描任务的唯一标识符。

### 扫描配置管理 (`scan_profiles`)

此模块用于列出并查看可用的扫描配置文件。

#### 列出扫描配置 (`list`)
列出所有扫描配置。

**用法:**
```bash
python examples/cli/main_cli.py scan_profiles list
```

#### 获取扫描配置详情 (`get`)
获取指定扫描配置 ID 的详细信息。

**用法:**
```bash
python examples/cli/main_cli.py scan_profiles get <扫描配置ID>
```

---

### 目标组管理 (`target_groups`)

此模块用于创建、更新及维护目标组。

#### 列出目标组 (`list`)
```bash
python examples/cli/main_cli.py target_groups list [--limit <数量>]
```

#### 创建目标组 (`create`)
```bash
python examples/cli/main_cli.py target_groups create <名称> [--description <描述>]
```

#### 获取目标组详情 (`get`)
```bash
python examples/cli/main_cli.py target_groups get <目标组ID>
```

#### 更新目标组 (`update`)
```bash
python examples/cli/main_cli.py target_groups update <目标组ID> [--name <新名称>] [--description <新描述>]
```

#### 删除目标组 (`delete`)
```bash
python examples/cli/main_cli.py target_groups delete <目标组ID>
```

---

### 报告管理 (`reports`)

此模块用于生成并下载扫描报告。

#### 列出报告 (`list`)
```bash
python examples/cli/main_cli.py reports list [--limit <数量>]
```

#### 生成报告 (`generate`)
```bash
python examples/cli/main_cli.py reports generate <模板ID> <来源类型> <来源ID...>
```

#### 获取报告详情 (`get`)
```bash
python examples/cli/main_cli.py reports get <报告ID>
```

#### 删除报告 (`delete`)
```bash
python examples/cli/main_cli.py reports delete <报告ID>
```

---

### 报告模板 (`report_templates`)

仅支持查看模板信息。

#### 列出模板 (`list`)
```bash
python examples/cli/main_cli.py report_templates list
```

#### 获取模板详情 (`get`)
```bash
python examples/cli/main_cli.py report_templates get <模板ID>
```

---

### 用户管理 (`users`)

#### 列出用户 (`list`)
```bash
python examples/cli/main_cli.py users list [--limit <数量>]
```

#### 创建用户 (`create`)
```bash
python examples/cli/main_cli.py users create <邮箱> <名> <姓> <密码> [--send_invite_email]
```

#### 获取用户详情 (`get`)
```bash
python examples/cli/main_cli.py users get <用户ID>
```

#### 更新用户 (`update`)
```bash
python examples/cli/main_cli.py users update <用户ID> [--email <新邮箱>] ...
```

#### 删除用户 (`delete`)
```bash
python examples/cli/main_cli.py users delete <用户ID>
```

---

### 用户组管理 (`user_groups`)

#### 列出用户组 (`list`)
```bash
python examples/cli/main_cli.py user_groups list
```

#### 创建用户组 (`create`)
```bash
python examples/cli/main_cli.py user_groups create <名称>
```

(更多操作请使用 `--help` 查看)

---

### 角色管理 (`roles`)

#### 列出角色 (`list`)
```bash
python examples/cli/main_cli.py roles list
```

#### 创建角色 (`create`)
```bash
python examples/cli/main_cli.py roles create <名称> --permissions <perm1,perm2>
```

---

### 漏洞管理 (`vulnerabilities`)

#### 列出漏洞 (`list`)
```bash
python examples/cli/main_cli.py vulnerabilities list -q "severity:high"
```

#### 获取漏洞详情 (`get`)
```bash
python examples/cli/main_cli.py vulnerabilities get <漏洞ID>
```

#### 更新漏洞状态 (`update_status`)
```bash
python examples/cli/main_cli.py vulnerabilities update_status <漏洞ID> fixed --comment "已修复"
```

---

### 导出任务 (`exports`)

#### 列出导出类型 (`list_types`)
```bash
python examples/cli/main_cli.py exports list_types
```

#### 创建导出 (`create`)
```bash
python examples/cli/main_cli.py exports create <导出类型ID> vulnerabilities <漏洞ID>
```

---

### 通知配置 (`notifications`)

#### 列出通知 (`list`)
```bash
python examples/cli/main_cli.py notifications list
```

#### 创建通知 (`create`)
```bash
python examples/cli/main_cli.py notifications create "扫描完成" scan_completed --scope_type all --email_addresses admin@example.com
```

---

### 问题跟踪器 (`issue_trackers`)

#### 列出跟踪器 (`list`)
```bash
python examples/cli/main_cli.py issue_trackers list
```

#### 创建跟踪器 (`create`)
```bash
python examples/cli/main_cli.py issue_trackers create "我的Jira" --config_file jira.json
```

---

### WAF 集成 (`wafs`)

#### 列出 WAF (`list`)
```bash
python examples/cli/main_cli.py wafs list
```

#### 创建 WAF (`create`)
```bash
python examples/cli/main_cli.py wafs create "我的WAF" --config_file waf.json
```

---

### 排除时段 (`excluded_hours`)

#### 列出排除时段 (`list`)
```bash
python examples/cli/main_cli.py excluded_hours list
```

#### 创建排除时段 (`create`)
```bash
python examples/cli/main_cli.py excluded_hours create "周末不扫" '[true,false,...]'
```

---

### 代理配置 (`agents_config`)

#### 获取代理配置 (`get`)
```bash
python examples/cli/main_cli.py agents_config get
```

#### 获取注册令牌 (`get_token`)
```bash
python examples/cli/main_cli.py agents_config get_token
```

---

### 扫描代理 (`workers`)

#### 列出扫描代理 (`list`)
```bash
python examples/cli/main_cli.py workers list
```

#### 授权扫描代理 (`authorize`)
```bash
python examples/cli/main_cli.py workers authorize <WorkerID>
```

更多子命令请使用 `--help` 查看。

## 5. 示例

**1. 首次配置 API 凭据:**
```bash
python examples/cli/main_cli.py login --api_url https://my-awvs.example.com --api_key yourSecretApiKeyHere
```

**2. 列出前 5 个目标 (使用已保存的凭据):**
```bash
python examples/cli/main_cli.py targets list --limit 5
```

**3. 添加一个新目标:**
```bash
python examples/cli/main_cli.py targets add "http://newtarget.com" "这是一个新的测试目标" --criticality 30
```

**4. 针对目标 ID `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` 使用扫描配置 ID `11111111-1111-1111-1111-111111111111` 启动扫描:**
```bash
python examples/cli/main_cli.py scans start xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx 11111111-1111-1111-1111-111111111111
```

**5. 查看扫描 ID `yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy` 的状态:**
```bash
python examples/cli/main_cli.py scans status yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
```

**6. 获取扫描 ID `zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz` 的前 10 个漏洞:**
```bash
python examples/cli/main_cli.py scans results zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz --limit 10
```

## 6. 调试

使用 `--debug` 标志可以启用详细的日志输出，有助于排查连接或 API 调用问题：

```bash
python examples/cli/main_cli.py --debug targets list
```

调试模式将显示 SDK 和 CLI 的详细日志，包括 HTTP 请求和响应的详细信息。
