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
└── api/
├── index.py                  # /api - 服务信息
├── album/
│   └── index.py              # /api/album/* - 本子接口
├── photo/
│   └── index.py              # /api/photo/* - 章节接口
└── utils/
├── init.py           # 包初始化
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
| GET | `/api/album/{album_id}` | 获取本子详情（包含完整章节列表） | `/api/album/1220749` |
| GET | `/api/album?id={album_id}` | 获取本子详情（查询参数方式） | `/api/album?id=1220749` |

### 章节接口

| 方法 | 端点 | 说明 | 示例 |
|------|------|------|------|
| GET | `/api/photo/{photo_id}` | 获取章节图片列表 | `/api/photo/1220752` |
| GET | `/api/photo?id={photo_id}` | 获取章节图片列表（查询参数方式） | `/api/photo?id=1220752` |

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
curl https://your-project.edgeone.app/api/album/1220749

# 获取本子数据（查询参数方式）
curl https://your-project.edgeone.app/api/album?id=1220749

# 获取章节图片
curl https://your-project.edgeone.app/api/photo/1220752
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

🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

Star ⭐ 这个项目，以便及时获取更新！

```