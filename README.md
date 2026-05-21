# 链域 Lianyu Pro

一个基于 Vue 3 + Flask 的书签管理与网址导航系统。项目围绕“个人收藏管理 + 公共网址广场 + 管理后台”构建，支持用户注册登录、书签分类、公开分享、热门排行、全局搜索、反馈会话、AI 兴趣分析与后台内容审核。

![首页](图片/首页.png)

## 功能特性

- 用户体系：注册、登录、JWT 鉴权、个人资料与账号状态控制。
- 书签管理：新增、编辑、删除、分类管理、网址信息抓取、访问次数统计。
- 公开广场：展示全局公开网址和用户公开分享，支持分类筛选与关键词搜索。
- 热门排行：按日、周、月等周期统计热门网址，记录访问趋势。
- AI 分析：根据用户收藏分析兴趣标签、生成推荐网址，并支持 URL 安全性评估。
- 反馈与站内信：用户提交反馈，管理员回复后以会话/消息形式持续沟通。
- 管理后台：用户管理、内容管理、全局分类维护、待审核内容、数据统计、操作日志、AI 配置。
- 部署支持：内置 Nginx、systemd、生产环境变量示例和服务器初始化脚本。

## 页面预览

| 用户端 | 管理端 |
| --- | --- |
| ![用户书签管理](图片/用户书签管理页面.png) | ![管理员后台](图片/管理员后台功能界面.png) |
| ![公开广场](图片/公开广场.png) | ![数据统计](图片/管理员-数据统计.png) |
| ![热门榜单](图片/热门榜单.png) | ![待处理审核](图片/管理员-待处理审核.png) |

## 技术栈

**前端**

- Vue 3
- Vue Router
- Pinia
- Element Plus
- Axios
- ECharts
- Vite

**后端**

- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- Werkzeug ProxyFix
- BeautifulSoup4 / Requests
- SQLite，支持通过 `DATABASE_URL` 切换 MySQL
- Gunicorn

## 项目结构

```text
lianyu-pro/
├── backend/                  # Flask 后端服务
│   ├── app.py                # 应用入口，注册路由并执行迁移
│   ├── config.py             # 环境变量与数据库配置
│   ├── migrations/           # 轻量数据库迁移
│   ├── models/               # SQLAlchemy 数据模型
│   ├── routes/               # API 路由
│   ├── utils/                # 鉴权、爬取、AI 服务等工具
│   └── requirements.txt
├── frontend/                 # Vue 3 前端应用
│   ├── src/
│   │   ├── api/              # API 请求封装
│   │   ├── layouts/          # 用户端/管理端布局
│   │   ├── router/           # 路由与权限守卫
│   │   ├── stores/           # Pinia 状态
│   │   └── views/            # 页面视图
│   ├── package.json
│   └── vite.config.js
├── deploy/                   # 生产部署配置
├── 图片/                     # 项目截图
├── start.bat                 # Windows 一键启动
├── stop.bat                  # Windows 停止脚本
└── mysql_setup.py            # MySQL 初始化辅助脚本
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm

### Windows 一键启动

项目根目录提供了 `start.bat`，会自动检查环境、安装依赖并启动前后端：

```bat
start.bat
```

启动后访问：

- 前端地址：`http://localhost:3000`
- 后端地址：`http://127.0.0.1:5000`
- 默认管理员：`admin / admin123`

### 手动启动

启动后端：

```bash
cd backend
pip install -r requirements.txt
python app.py
```

启动前端：

```bash
cd frontend
npm install
npm run dev
```

Vite 已配置 `/api` 代理到 `http://127.0.0.1:5000`。

## 配置说明

后端会按顺序读取以下环境文件：

- `.env`
- `.env.local`
- `backend/.env`
- `backend/.env.local`

常用配置：

```env
SECRET_KEY=replace-with-a-random-secret
JWT_SECRET_KEY=replace-with-another-random-secret
DATABASE_URL=sqlite:///D:/path/to/lianyu-pro/backend/app.db
TRUSTED_PROXY_COUNT=1
```

默认使用 `backend/app.db` 作为 SQLite 数据库。需要切换 MySQL 时，可配置：

```env
DATABASE_URL=mysql+pymysql://user:password@127.0.0.1:3306/lianyu?charset=utf8mb4
```

AI 功能由管理员在后台的 AI 设置中配置接口地址、API Key 和模型名称；未配置时，普通书签管理功能不受影响。

## 后端 API 模块

- `/api/auth`：注册、登录、退出、用户信息。
- `/api/bookmarks`：书签 CRUD、公开广场、排行、访问记录、审核提交。
- `/api/categories`：用户分类管理。
- `/api/user`：个人中心、设置、反馈相关用户侧接口。
- `/api/admin`：后台用户、内容、分类、统计、日志、反馈、AI 配置。
- `/api/ai`：兴趣分析、网址推荐、URL 安全评估。

## 部署

`deploy/` 目录提供了生产部署参考：

- `server_setup.sh`：服务器初始化脚本。
- `lianyu.nginx.conf`：Nginx 反向代理配置。
- `lianyu-backend.service`：systemd 后端服务配置。
- `.env.production.example`：生产环境变量模板。
- `部署指南.md`：更完整的部署步骤。

典型生产方式是：前端执行 `npm run build` 生成静态资源，由 Nginx 托管；后端使用 Gunicorn + systemd 运行，并通过 Nginx 代理 `/api`。

## 测试

后端包含基础测试用例，例如真实 IP / 代理头处理相关测试：

```bash
cd backend
python -m pytest
```

前端可执行构建检查：

```bash
cd frontend
npm run build
```

## 默认账号

首次启动后，系统会自动创建管理员账号：

```text
用户名：admin
密码：admin123
```

上线部署前请登录后台修改默认密码，并配置强随机的 `SECRET_KEY` 与 `JWT_SECRET_KEY`。

## 项目亮点

- 前后端分离架构清晰，开发环境通过 Vite 代理实现无感联调。
- 用户书签和全局公开网址共存，既能做个人收藏夹，也能做网址导航站。
- 后台具备审核、屏蔽、统计、日志、反馈回复等完整管理闭环。
- 数据库默认开箱即用，同时保留 MySQL 生产化扩展路径。
- AI 能力通过后台配置接入，避免把模型服务绑定死在代码中。
