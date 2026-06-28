# Jmcomic API

> 基于 EdgeOne Pages Functions 的禁漫天堂数据 API 服务

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![EdgeOne Pages](https://img.shields.io/badge/EdgeOne-Pages-orange.svg)](https://pages.edgeone.ai/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)


## 📖 项目简介

Jmcomic API 是一个部署在 EdgeOne Pages 上的 Serverless API 服务，提供禁漫天堂（JMComic）的数据查询接口。通过模拟移动端 API 请求，自动获取最新可用域名，并对响应数据进行 AES 解密，以 RESTful API 形式对外提供服务。

### ✨ 核心特性

- 🔄 自动获取域名：从域名服务器动态获取最新可用 API 域名
- 🔐 请求签名：自动生成 Token 和 tokenparam 进行身份认证
- 🔓 响应解密：自动解密 AES-ECB 加密的 API 响应数据
- 🌐 中文支持：正确解码 GBK 编码的中文内容
- 🚀 Serverless 部署：基于 EdgeOne Pages，零配置部署，自动扩缩容
- 📦 轻量依赖：仅依赖 requests 和 pycryptodome


## 🏗️ 项目结构

```

cloud-functions/
├── api/
│   ├── index.py
│   ├── album/
│   │   └── index.py
│   ├── photo/
│   │   └── index.py
│   └── utils/
│       ├── __init__.py
│       ├── client.py
│       ├── crypto.py
│       ├── models.py
│       └── parser.py
└── requirements.txt

```


## 📡 API 接口文档

### 一、服务信息

- 端点：GET /api
- 说明：获取 API 服务的基本信息和可用接口列表

响应示例：
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

二、获取本子详情

- 端点：GET /api/album/{album_id} 或 GET /api/album?id={album_id}
- 说明：获取指定本子的详细信息，包括作者、标签、章节列表等

⚠️ 重要：album_id 必须是禁漫车号（本子 ID）

- ✅ 正确示例：/api/album/179377（179377 是禁漫车号）
- ❌ 错误示例：/api/album/179378（179378 是禁漫号，不是车号）

请求参数：

- id（必填）：禁漫车号，纯数字

响应示例：

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

错误码说明：

- 400：album_id 必须是纯数字
- 404：本子不存在
- 429：请求过于频繁
- 504：请求超时
- 500：服务器内部错误

三、获取章节图片

- 端点：GET /api/photo/{photo_id} 或 GET /api/photo?id={photo_id}
- 说明：获取指定章节的图片列表，返回图片 CDN 链接

⚠️ 重要：photo_id 可以是禁漫车号或禁漫号

- 传入禁漫车号（如 179377）：返回该本子第一个章节的图片列表
- 传入禁漫号（如 179378）：返回该具体章节的图片列表

请求参数：

- id（必填）：禁漫号或禁漫车号，纯数字

响应示例：

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
    ]
  }
}
```

错误码说明：

- 400：photo_id 必须是纯数字
- 404：章节不存在
- 429：请求过于频繁
- 504：请求超时
- 500：服务器内部错误

📊 数据模型说明

禁漫车号（Album ID）

- 定义：本子的唯一标识符，也称"车号"
- 特征：纯数字，如 179377
- 用途：用于 /api/album 接口获取本子详情
- 示例：/api/album/179377

禁漫号（Photo ID）

- 定义：章节的唯一标识符，也称"章节号"
- 特征：纯数字，如 179378
- 用途：用于 /api/photo 接口获取章节图片
- 示例：/api/photo/179378

关系说明

```
禁漫车号（Album ID）≠ 禁漫号（Photo ID）

禁漫车号 = 179377（本子标识符）
    │
    ├── 禁漫号 = 179378（第1话）
    ├── 禁漫号 = 179379（第2话）
    └── 禁漫号 = 179380（第3话）
```

接口兼容性

- 禁漫车号（如 179377）→ /api/album：✅ 可以，/api/photo：✅ 可以（返回第一话）
- 禁漫号（如 179378）→ /api/album：❌ 不可以，/api/photo：✅ 可以

推荐使用流程

1. 先调用 /api/album/{车号} 获取本子信息和章节列表
2. 从响应的 photos 数组中提取每个章节的 photo_id
3. 再调用 /api/photo/{禁漫号} 获取具体章节的图片

🚨 错误处理

所有接口返回统一的错误格式：

```json
{
  "code": <HTTP状态码>,
  "error": "<错误描述>"
}
```

错误码说明：

- 400：请求参数错误，检查参数格式是否为纯数字
- 404：资源不存在，检查 ID 是否正确
- 429：请求过于频繁，降低请求频率，稍后重试
- 504：请求超时，稍后重试
- 500：服务器内部错误，联系管理员

🚀 部署指南

准备工作

- EdgeOne Pages 账号
- Git 仓库（GitHub / GitLab / Gitee）

部署步骤

1. Fork 或克隆本项目到您的 Git 仓库
2. 登录 EdgeOne Pages 控制台（pages.edgeone.ai）
3. 点击「创建项目」，选择「从 Git 仓库部署」
4. 授权并选择您的仓库
5. 构建配置全部留空（平台自动检测）
6. 点击「部署」，平台会自动检测 cloud-functions/ 目录并安装依赖
7. 部署成功后，会生成类似 https://your-project.edgeone.app 的域名

验证部署

```bash
# 测试服务是否正常
curl https://your-project.edgeone.app/api

# 获取本子数据
curl https://your-project.edgeone.app/api/album/179377

# 获取章节图片
curl https://your-project.edgeone.app/api/photo/179378
```

🔧 本地开发

环境要求

- Python 3.10+
- pip

安装依赖

```bash
pip install -r requirements.txt
```

本地测试

```bash
cd cloud-functions/api
python -c "from utils.client import JmClient; print('OK')"
```

🛠️ 技术架构

核心模块

- Client（client.py）：API 请求客户端，支持重试、域名切换、Token 生成
- Parser（parser.py）：数据解析器，处理中文编码和 CDN URL 构建
- Crypto（crypto.py）：加密/解密工具，处理 API 数据和域名解密
- Models（models.py）：数据模型定义（JmAlbum、JmPhoto、JmImage）

技术栈

- 运行时：Python 3.x（EdgeOne Pages Functions）
- HTTP 客户端：requests
- 加密库：pycryptodome（AES-ECB）
- 部署平台：EdgeOne Pages Functions

关键特性

1. 自动域名切换：从域名服务器获取可用域名列表，失败时自动切换
2. 智能重试：支持指数退避重试，应对限流和网络波动
3. Token 生成：自动生成 API 访问 Token
4. 数据解密：自动解密禁漫 API 返回的加密数据
5. 中文编码：正确处理 GBK/UTF-8 编码的中文文本

⚙️ 配置说明

配置参数位于 client.py 的 Config 类中：

```python
class Config:
    DOMAIN_SERVERS = [...]        # 域名服务器地址
    FALLBACK_DOMAINS = [...]      # 降级域名列表
    RETRY_TIMES = 3               # 重试次数
    TIMEOUT = 30                  # 超时时间（秒）
    RETRY_DELAY_BASE = 1          # 重试基础延迟
    RETRY_MAX_DELAY = 10          # 最大延迟
    IP_POOL = [...]               # IP 池（用于 X-Forwarded-For）
```

📝 注意事项

1. 合规使用：请遵守相关法律法规，仅用于学习和研究目的
2. 频率限制：建议控制请求频率，避免触发限流
3. ID 类型：务必区分禁漫车号和禁漫号，避免用错接口
4. SSL 验证：当前实现禁用了 SSL 验证（生产环境建议启用）
5. 域名缓存：域名列表缓存 1 小时，减少域名服务器请求

## 参考及感谢以下项目

### 禁漫Python爬虫

<a href="https://github.com/hect0x7/JMComic-Crawler-Python">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api/pin/?username=hect0x7&repo=JMComic-Crawler-Python&theme=radical" />
    <source media="(prefers-color-scheme: light)" srcset="https://github-readme-stats.vercel.app/api/pin/?username=hect0x7&repo=JMComic-Crawler-Python" />
    <img alt="Repo Card" src="https://github-readme-stats.vercel.app/api/pin/?username=hect0x7&repo=JMComic-Crawler-Python" />
  </picture>
</a>

📄 License

MIT License

⚠️ 免责声明

1. 本项目仅供学习和研究使用
2. 请勿用于任何商业用途或侵犯他人权益
3. 使用者需自行承担使用风险
4. 本项目作者不对因使用本项目造成的任何后果负责


