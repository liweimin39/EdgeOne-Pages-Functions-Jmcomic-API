# Jmcomic API

> 基于 EdgeOne Pages 的禁漫天堂数据 API 服务

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![EdgeOne Pages](https://img.shields.io/badge/EdgeOne-Pages-orange.svg)](https://pages.edgeone.ai/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📖 项目简介

Jmcomic API 是一个部署在 **EdgeOne Pages** 上的 Serverless API 服务，提供禁漫天堂（JMComic）的数据查询接口。通过模拟移动端 API 请求，自动获取最新可用域名，并对响应数据进行 AES 解密，将数据以 RESTful API 的形式对外提供。

### ✨ 核心特性

- 🔄 **自动获取域名**：从域名服务器动态获取最新可用 API 域名
- 🔐 **请求签名**：自动生成 Token 和 tokenparam 进行身份认证
- 🔓 **响应解密**：自动解密 AES-ECB 加密的 API 响应数据
- 🌐 **中文支持**：正确解码 GBK 编码的中文内容
- 🚀 **Serverless 部署**：基于 EdgeOne Pages，零配置部署，自动扩缩容
- 📦 **轻量依赖**：仅依赖 `requests` 和 `pycryptodome`

## 🏗️ 项目结构

```

cloud-functions/
├── requirements.txt              # Python 依赖
└── api/                          # API 根目录
    ├── index.py                  # /api - 服务信息
    ├── album/
    │   └── index.py              # /api/album/* - 本子接口
    ├── photo/
    │   └── index.py              # /api/photo/* - 章节接口
    └── utils/                    # 工具模块（在 api 内部）
        ├── __init__.py           # 包初始化
        ├── client.py             # HTTP 客户端（域名获取、请求签名）
        ├── parser.py             # 数据解析器（中文解码）
        ├── crypto.py             # 加密工具（AES 解密、Token 生成）
        └── models.py             # 数据模型定义

```

## 📡 API 端点

### 基础信息

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api` | 服务信息，列出所有可用端点 |

### 本子接口

| 方法 | 端点 | 说明 | 示例 |
|------|------|------|------|
| GET | `/api/album/{album_id}` | 获取本子详情（包含完整章节列表） | `/api/album/{album_id}` |
| GET | `/api/album?id={album_id}` | 获取本子详情（查询参数方式） | `/api/album?id={album_id}` |

### 章节接口

| 方法 | 端点 | 说明 | 示例 |
|------|------|------|------|
| GET | `/api/photo/{photo_id}` | 获取章节图片列表 | `/api/photo/1220752` |
| GET | `/api/photo?id={photo_id}` | 获取章节图片列表（查询参数方式） | `/api/photo?id={photo_id}` |

## 📊 响应格式

### 本子详情响应

```json
{
  "code": 200,
  "data": {
    "album_id": "JM号",
    "album_title": "标题",
    "author": "未知",
    "authors": [],
    "tags": ["标签"],
    "cover_url": "https://cdn-msp.jmapiproxy2.cc/media/photos/JM号/cover.jpg",
    "views": "观看人数",
    "likes": "喜欢人数",
    "total_photos": 31,
    "photos": [
      {
        "photo_id": "章节1JM号",
        "title": "",
        "sort": 1,
        "image_count": 0
      },
      {
        "photo_id": "章节2JM号",
        "title": "",
        "sort": 2,
        "image_count": 60
      }
    ]
  }
}
```

章节详情响应

```json
{
  "code": 200,
  "data": {
    "photo_id": "JM号",
    "title": "标题",
    "image_count": 60,
    "images": [
      {
        "index": 1,
        "filename": "图片ID.webp",
        "url": "https://cdn-msp.jmapiproxy1.cc/media/photos/JM号/图片ID.webp"
      }
    ]
  }
}
```

🚀 部署指南

1. 准备工作

· EdgeOne Pages 账号
· Git 仓库（GitHub / GitLab / Gitee）

2. 部署步骤

1. Fork 或克隆本项目 到您的 Git 仓库
2. 登录 EdgeOne Pages 控制台
   · 进入 EdgeOne Pages
   · 点击「创建项目」
3. 连接 Git 仓库
   · 选择「从 Git 仓库部署」
   · 授权并选择您的仓库
4. 配置构建选项
   · 构建命令：留空（自动检测）
   · 输出目录：留空
   · 环境变量：无需配置
5. 点击「部署」
   · 平台会自动检测 cloud-functions/ 目录
   · 自动安装依赖并部署
6. 获取访问域名
   · 部署成功后，会生成类似 https://your-project.edgeone.app 的域名

3. 验证部署

```bash
# 测试服务是否正常
curl https://your-project.edgeone.app/api

# 获取本子数据（路径方式）
curl https://your-project.edgeone.app/api/album/{album_id}

# 获取本子数据（查询参数方式）
curl https://your-project.edgeone.app/api/album?id={album_id}

# 获取章节图片（路径方式）
curl https://your-project.edgeone.app/api/photo/{photo_id}

# 获取章节图片（查询参数方式）
curl https://your-project.edgeone.app/api/photo?id={photo_id}
```

🔧 本地开发

环境要求

· Python 3.10+
· pip

安装依赖

```bash
pip install -r requirements.txt
```

本地测试

```bash
# 进入 api 目录
cd cloud-functions/api

# 测试模块导入
python -c "from utils.client import JmClient; print('OK')"
```

📝 配置说明

域名服务器

项目会自动从以下域名服务器获取最新 API 域名：

```python
DOMAIN_SERVERS = [
    'https://rup4a04-c01.tos-ap-southeast-1.bytepluses.com/newsvr-2025.txt',
    'https://rup4a04-c02.tos-cn-hongkong.bytepluses.com/newsvr-2025.txt',
]
```

请求头配置

模拟移动端 APP 请求，包含必要的认证头：

```python
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) ...',
    'X-Requested-With': 'com.JMComic3.app',
    'token': '{timestamp+secret_md5}',
    'tokenparam': '{timestamp},{app_version}',
}
```

🛠️ 技术实现

1. 域名获取

```python
def _get_domains(self) -> list:
    # 从域名服务器获取加密的域名列表
    response = self.session.get(server_url)
    # 解密得到可用域名
    return JmCrypto.decrypt_domain_data(response.text)
```

2. 请求签名

```python
def generate_token(timestamp: str) -> tuple:
    token_param = f'{timestamp},{APP_VERSION}'
    token = md5hex(f'{timestamp}{APP_TOKEN_SECRET}')
    return token, token_param
```

3. 响应解密

```python
def decrypt_api_data(encrypted_data: str, timestamp: str) -> str:
    # Base64 解码
    encrypted_bytes = base64.b64decode(encrypted_data)
    # AES-ECB 解密
    key = md5hex(f'{timestamp}{APP_DATA_SECRET}')
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(encrypted_bytes)
    # 移除 PKCS7 填充
    return decrypted[:-decrypted[-1]].decode('utf-8')
```

4. 中文解码

禁漫 API 返回的是 GBK 编码，需要正确转换：

```python
def _decode_chinese(text: str) -> str:
    return text.encode('latin1').decode('gbk')
```

📄 License

MIT

⚠️ 免责声明

1. 本项目仅供学习和研究使用
2. 请勿用于任何商业用途或侵犯他人权益
3. 使用者需自行承担使用风险
4. 本项目作者不对因使用本项目造成的任何后果负责

# Jmcomic API - EdgeOne Pages Functions

基于 EdgeOne Pages Functions 部署的禁漫天堂数据 API 服务，提供本子信息和章节图片的获取接口。

## 📖 目录

- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
  - [本地开发](#本地开发)
  - [部署到 EdgeOne Pages](#部署到-edgeone-pages)
- [API 接口文档](#api-接口文档)
  - [服务信息](#服务信息)
  - [获取本子详情](#获取本子详情)
  - [获取章节图片](#获取章节图片)
- [数据模型说明](#数据模型说明)
  - [禁漫车号 (Album ID)](#禁漫车号-album-id)
  - [禁漫号 (Photo ID)](#禁漫号-photo-id)
  - [关系说明](#关系说明)
- [错误处理](#错误处理)
- [技术架构](#技术架构)
- [配置说明](#配置说明)
- [注意事项](#注意事项)
- [参考及感谢](#参考及感谢以下项目)

---

## ✨ 功能特性

- 🚀 基于 EdgeOne Pages Functions 无服务器部署
- 📦 获取本子（Album）详情及章节列表
- 🖼️ 获取章节（Photo）图片列表及 CDN 链接
- 🔐 内置禁漫 API 加密/解密支持
- 🔄 自动域名切换与重试机制
- 🛡️ 支持 CORS 跨域请求
- 📝 完整的错误处理和日志记录

---

## 📁 项目结构

```

cloud-functions/
├── api/
│   ├── index.py                    # /api - 服务信息
│   ├── album/
│   │   └── index.py                # /api/album - 本子详情
│   ├── photo/
│   │   └── index.py                # /api/photo - 章节图片
│   └── utils/
│       ├── init.py
│       ├── client.py               # API 客户端（含重试、域名切换）
│       ├── parser.py               # 数据解析器
│       ├── crypto.py               # 加密/解密工具
│       └── models.py               # 数据模型定义
├── requirements.txt                # Python 依赖
└── README.md                       # 项目文档

```

---

## 🚀 快速开始

### 本地开发

1. **克隆项目**
```bash
git clone <your-repo-url>
cd <project-directory>
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 本地测试
   由于 EdgeOne Pages Functions 使用 Python 运行时，你可以使用任何支持 WSGI 的服务器进行测试，或使用 EdgeOne Pages CLI 进行本地模拟。

部署到 EdgeOne Pages

1. 将项目推送到 Git 仓库
2. 在 EdgeOne Pages 控制台创建项目，关联你的 Git 仓库
3. 配置构建命令（如有需要）
4. 部署完成后，即可通过 https://your-domain.com/api 访问服务

---

📡 API 接口文档

服务信息

端点: GET /api

获取 API 服务的基本信息和可用接口列表。

响应示例:

```json
{
  "service": "Jmcomic API",
  "version": "2.0.0",
  "description": "禁漫天堂数据 API 服务",
  "endpoints": {
    "album": {
      "description": "获取本子详情",
      "methods": ["GET"],
      "usage": "/api/album/{album_id} 或 /api/album?id={album_id}"
    },
    "photo": {
      "description": "获取章节图片列表",
      "methods": ["GET"],
      "usage": "/api/photo/{photo_id} 或 /api/photo?id={photo_id}"
    }
  }
}
```

---

获取本子详情

端点: GET /api/album/{album_id} 或 GET /api/album?id={album_id}

获取指定本子的详细信息，包括作者、标签、章节列表等。

⚠️ 重要说明

album_id 必须是禁漫车号，即本子的唯一标识符。

· ✅ 正确: /api/album/179377 (179377 是禁漫车号)
· ❌ 错误: /api/album/179378 (179378 是禁漫号，不是车号)

请求参数

参数 类型 必填 说明
id string ✅ 禁漫车号 (纯数字)

响应示例

```json
{
  "code": 200,
  "data": {
    "album_id": "179377",
    "album_title": "示例本子标题",
    "author": "作者名",
    "authors": ["作者名1", "作者名2"],
    "tags": ["标签1", "标签2"],
    "cover_url": "https://cdn.xxx.com/media/photos/179377/cover.jpg",
    "views": "12345",
    "likes": "678",
    "page_count": 32,
    "description": "本子描述信息",
    "total_photos": 5,
    "photos": [
      {
        "photo_id": "179378",
        "title": "第1话",
        "sort": 1
      },
      {
        "photo_id": "179379",
        "title": "第2话",
        "sort": 2
      }
    ]
  }
}
```

错误响应

状态码 说明
400 album_id 必须是纯数字
404 本子不存在
429 请求过于频繁
504 请求超时
500 服务器内部错误

---

获取章节图片

端点: GET /api/photo/{photo_id} 或 GET /api/photo?id={photo_id}

获取指定章节的图片列表，返回图片 CDN 链接。

⚠️ 重要说明

photo_id 可以是禁漫车号或禁漫号：

· 传入禁漫车号 (如 179377)：返回该本子第一章节的图片列表
· 传入禁漫号 (如 179378)：返回该章节的图片列表

即：photo_id 参数接受禁漫车号或禁漫号，系统会自动识别并返回对应章节的图片。

请求参数

参数 类型 必填 说明
id string ✅ 禁漫号或禁漫车号 (纯数字)

响应示例

```json
{
  "code": 200,
  "data": {
    "photo_id": "179378",
    "title": "第1话",
    "image_count": 28,
    "images": [
      {
        "index": 1,
        "filename": "001.jpg",
        "url": "https://cdn.xxx.com/media/photos/179378/001.jpg"
      },
      {
        "index": 2,
        "filename": "002.jpg",
        "url": "https://cdn.xxx.com/media/photos/179378/002.jpg"
      }
      // ...
    ]
  }
}
```

错误响应

状态码 说明
400 photo_id 必须是纯数字
404 章节不存在
429 请求过于频繁
504 请求超时
500 服务器内部错误

---

📊 数据模型说明

禁漫车号 (Album ID)

· 定义: 本子的唯一标识符，也称"车号"
· 特征: 纯数字，如 179377
· 用途: 用于 /api/album 接口获取本子详情
· 示例: /api/album/179377

禁漫号 (Photo ID)

· 定义: 章节的唯一标识符，也称"章节号"
· 特征: 纯数字，如 179378
· 用途: 用于 /api/photo 接口获取章节图片
· 示例: /api/photo/179378

关系说明

```
禁漫车号 (Album ID)  ≠  禁漫号 (Photo ID)
    │                            │
    │  包含关系                   │  独立标识
    ▼                            ▼
 本子标识符                   章节标识符
 (如: 179377)                (如: 179378)
    │
    └── 包含多个章节 ──► 每个章节有独立的禁漫号
                           (如: 179378, 179379, ...)
```

核心规则:

标识符类型 是否可用于 /api/album 是否可用于 /api/photo
禁漫车号 (179377) ✅ 可以 ✅ 可以 (返回第一个章节)
禁漫号 (179378) ❌ 不可以 ✅ 可以

使用建议:

1. 先通过 /api/album/{车号} 获取本子信息和章节列表
2. 从响应中的 photos 数组获取每个章节的 photo_id
3. 使用 /api/photo/{禁漫号} 获取具体章节的图片

---

🚨 错误处理

所有接口返回统一的错误格式：

```json
{
  "code": <HTTP状态码>,
  "error": "<错误描述>"
}
```

错误码 说明 处理建议
400 请求参数错误 检查参数格式
404 资源不存在 检查 ID 是否正确
429 请求过于频繁 降低请求频率，稍后重试
504 请求超时 稍后重试
500 服务器内部错误 联系管理员

---

🏗️ 技术架构

核心模块

模块 功能 文件
Client API 请求客户端，支持重试、域名切换、Token 生成 client.py
Parser 数据解析器，处理中文编码和 CDN URL 构建 parser.py
Crypto 加密/解密工具，处理 API 数据和域名解密 crypto.py
Models 数据模型定义 (JmAlbum, JmPhoto, JmImage) models.py

技术栈

· 运行时: Python 3.x (EdgeOne Pages Functions)
· HTTP 客户端: requests
· 加密库: pycryptodome (AES-ECB)
· 部署平台: EdgeOne Pages Functions

关键特性

1. 自动域名切换: 从域名服务器获取可用域名列表，失败时自动切换
2. 智能重试: 支持指数退避重试，应对限流和网络波动
3. Token 生成: 自动生成 API 访问 Token
4. 数据解密: 自动解密禁漫 API 返回的加密数据
5. 中文编码: 正确处理 GBK/UTF-8 编码的中文文本

---

⚙️ 配置说明

配置参数位于 client.py 的 Config 类中：

```python
class Config:
    DOMAIN_SERVERS = [...]        # 域名服务器地址
    FALLBACK_DOMAINS = [...]      # 降级域名列表
    RETRY_TIMES = 3               # 重试次数
    TIMEOUT = 30                  # 超时时间 (秒)
    RETRY_DELAY_BASE = 1          # 重试基础延迟
    RETRY_MAX_DELAY = 10          # 最大延迟
    IP_POOL = [...]               # IP 池 (用于 X-Forwarded-For)
```

---

📝 注意事项

1. 合规使用: 请遵守相关法律法规，仅用于学习和研究目的
2. 频率限制: 建议控制请求频率，避免触发限流
3. ID 类型: 务必区分禁漫车号和禁漫号，避免用错接口
4. SSL 验证: 当前实现禁用了 SSL 验证 (生产环境建议启用)
5. 缓存: 域名列表缓存 1 小时，减少域名服务器请求

---

## 参考及感谢以下项目


<a href="https://github.com/hect0x7/JMComic-Crawler-Python">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api/pin/?username=hect0x7&repo=JMComic-Crawler-Python&theme=radical" />
    <source media="(prefers-color-scheme: light)" srcset="https://github-readme-stats.vercel.app/api/pin/?username=hect0x7&repo=JMComic-Crawler-Python" />
    <img alt="Repo Card" src="https://github-readme-stats.vercel.app/api/pin/?username=hect0x7&repo=JMComic-Crawler-Python" />
  </picture>
</a>
---

注意: 本项目仅供学习参考，请勿用于商业用途或侵犯他人权益。使用本 API 即表示您同意遵守相关法律法规和服务条款。