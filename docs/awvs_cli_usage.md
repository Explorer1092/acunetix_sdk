# Acunetix AWVS CLI (`awvs_cli.py`) 用法指南

`awvs_cli.py` 是一个命令行工具，用于通过 Acunetix API 与您的 Acunetix AWVS (Acunetix Web Vulnerability Scanner) 实例进行交互。它允许您管理扫描目标、启动和管理扫描任务以及检索扫描结果。

## 目录
- [Acunetix AWVS CLI (`awvs_cli.py`) 用法指南](#acunetix-awvs-cli-awvs_clipy-用法指南)
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
  - [5. 示例](#5-示例)

## 1. 先决条件

*   Python 3.x
*   已安装 `acunetix_sdk` 包 (通常此脚本位于 SDK 的 `examples` 目录中，因此 SDK 应已可用)
*   可以访问您的 Acunetix AWVS 实例 API。

## 2. 配置凭据

您可以通过以下任一方式配置 `awvs_cli.py` 连接到 Acunetix API 所需的凭据：

### 使用 `login` 命令 (推荐)
这是推荐的配置方式，它会将您的 API URL 和 API Key 保存到一个本地配置文件中，供后续命令使用。

**用法:**
```bash
python examples/awvs_cli.py login <API_URL> <API_KEY>
```
*   `<API_URL>`: 您的 Acunetix API 的完整 URL (例如, `https://your-acunetix-instance.com`)。
*   `<API_KEY>`: 您的 Acunetix API 密钥。

执行此命令后，凭据将保存在配置文件中。

### 使用环境变量
如果您不想使用配置文件，或者想临时覆盖配置文件中的设置，可以设置以下环境变量：

*   `AWVS_API_URL`: 您的 Acunetix API 的完整 URL。
*   `AWVS_API_KEY`: 您的 Acunetix API 密钥。

**示例 (bash):**
```bash
export AWVS_API_URL="https://your-acunetix-instance.com"
export AWVS_API_KEY="your_api_key_here"
# 然后运行脚本
python examples/awvs_cli.py targets list
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
python examples/awvs_cli.py [模块] [操作] [参数...]
```

您可以使用 `--help` 选项查看通用帮助信息或特定模块/操作的帮助：

```bash
python examples/awvs_cli.py --help
python examples/awvs_cli.py login --help
python examples/awvs_cli.py targets --help
python examples/awvs_cli.py targets add --help
```

## 4. 模块和操作

### 登录配置 (`login`)
保存 Acunetix API URL 和 API Key 到本地配置文件，以便后续命令使用，无需每次都设置环境变量。

**用法:**
```bash
python examples/awvs_cli.py login <API_URL> <API_KEY>
```
*   `<API_URL>` (必需): 您的 Acunetix API 的完整 URL (例如 `https://acunetix.example.com`)。
*   `<API_KEY>` (必需): 您的 Acunetix API 密钥。

执行后，凭据将保存到 `~/.config/awvs_cli/config.json`。

---

### 目标管理 (`targets`)

此模块用于管理扫描目标。

#### 列出目标 (`list`)
列出所有已配置的目标。

**用法:**
```bash
python examples/awvs_cli.py targets list [--limit <数量>]
```
*   `--limit <数量>` (可选): 限制返回的目标数量。默认为 100。

#### 添加目标 (`add`)
添加一个新的扫描目标。

**用法:**
```bash
python examples/awvs_cli.py targets add <地址> <描述> [--criticality <重要性>]
```
*   `<地址>` (必需): 目标地址 (例如 `http://example.com`, `https://test.com`)。
*   `<描述>` (必需): 目标的描述性文本。
*   `--criticality <重要性>` (可选): 目标的重要性级别，范围从 0 到 100，必须是 10 的倍数 (例如 10, 20, ..., 100)。默认为 10。

#### 删除目标 (`delete`)
根据目标 ID 删除一个目标。

**用法:**
```bash
python examples/awvs_cli.py targets delete <目标ID>
```
*   `<目标ID>` (必需): 要删除的目标的唯一标识符。

---

### 扫描管理 (`scans`)

此模块用于管理扫描任务。

#### 启动扫描 (`start`)
针对指定的目标启动一个新的扫描任务。

**用法:**
```bash
python examples/awvs_cli.py scans start <目标ID> <扫描配置ID>
```
*   `<目标ID>` (必需): 要扫描的目标的唯一标识符。
*   `<扫描配置ID>` (必需): 用于扫描的扫描配置文件的唯一标识符 (例如, 全面扫描的默认 ID 通常是 `11111111-1111-1111-1111-111111111111`)。

#### 列出扫描 (`list`)
列出所有扫描任务。

**用法:**
```bash
python examples/awvs_cli.py scans list [--limit <数量>]
```
*   `--limit <数量>` (可选): 限制返回的扫描任务数量。默认为 20。

#### 获取扫描状态 (`status`)
获取特定扫描任务的当前状态和进度。

**用法:**
```bash
python examples/awvs_cli.py scans status <扫描ID>
```
*   `<扫描ID>` (必需): 要查询状态的扫描任务的唯一标识符。

#### 获取扫描结果 (`results`)
获取特定扫描任务发现的漏洞列表。

**用法:**
```bash
python examples/awvs_cli.py scans results <扫描ID> [--limit <数量>]
```
*   `<扫描ID>` (必需): 要获取结果的扫描任务的唯一标识符。
*   `--limit <数量>` (可选): 限制返回的漏洞数量。默认为 100。

#### 中止扫描 (`stop`)
中止一个正在进行的扫描任务。

**用法:**
```bash
python examples/awvs_cli.py scans stop <扫描ID>
```
*   `<扫描ID>` (必需): 要中止的扫描任务的唯一标识符。

#### 删除扫描 (`delete`)
删除一个扫描任务的记录。

**用法:**
```bash
python examples/awvs_cli.py scans delete <扫描ID>
```
*   `<扫描ID>` (必需): 要删除的扫描任务的唯一标识符。

## 5. 示例

**1. 首次配置 API 凭据:**
```bash
python examples/awvs_cli.py login https://my-awvs.example.com yourSecretApiKeyHere
```

**2. 列出前 5 个目标 (使用已保存的凭据):**
```bash
python examples/awvs_cli.py targets list --limit 5
```

**3. 添加一个新目标:**
```bash
python examples/awvs_cli.py targets add "http://newtarget.com" "这是一个新的测试目标" --criticality 30
```

**4. 针对目标 ID `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` 使用全扫描配置启动扫描:**
```bash
python examples/awvs_cli.py scans start xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx 11111111-1111-1111-1111-111111111111
```

**5. 查看扫描 ID `yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy` 的状态:**
```bash
python examples/awvs_cli.py scans status yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
```

**6. 获取扫描 ID `zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz` 的前 10 个漏洞:**
```bash
python examples/awvs_cli.py scans results zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz --limit 10
