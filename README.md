# my-vue-graph-app

## 项目简介
my-vue-graph-app 是一个基于 Vue 3 和 Flask 的智能知识图谱问答系统。该项目结合了前端可视化和后端智能处理，支持自然语言到 Cypher 查询的转换、知识图谱的动态展示以及多种交互功能。

## 功能特性
- **知识图谱可视化**：支持节点和边的动态展示，提供多种布局和样式编辑功能。
- **自然语言查询**：通过后端 AI 模型，将自然语言问题转换为 Cypher 查询。
- **时间轴筛选**：通过时间轴组件筛选图谱数据。
- **多媒体资源展示**：支持展示与节点相关的图片和视频。
- **缓存优化**：后端支持多级缓存（内存 + Redis），提升查询性能。
- **健康检查与管理**：提供健康检查和缓存管理的 API。

## 技术栈
### 前端
- Vue 3
- Vite
- Element Plus
- @vueuse/core

### 后端
- Flask
- Neo4j
- Redis

## 目录结构
```
my-vue-graph-app/
├── backend/                # 后端代码
│   ├── agent.py           # 智能代理逻辑
│   ├── app.py             # Flask 应用主入口
│   ├── cache.py           # 缓存管理
│   ├── config.py          # 配置文件
│   ├── neo4j_driver.py    # Neo4j 驱动
│   ├── utils.py           # 工具函数
├── public/                 # 静态资源
├── src/                    # 前端代码
│   ├── App.vue            # 主应用组件
│   ├── main.js            # 应用入口
│   ├── components/        # 子组件
│   │   ├── AIChat.vue     # AI 聊天组件
│   │   ├── GraphChart.vue # 图表组件
│   │   ├── TimeSlider.vue # 时间轴组件
│   │   ├── ...            # 其他组件
│   ├── utils/             # 工具函数
│   │   ├── formatters.js  # 格式化工具
├── index.html              # HTML 模板
├── package.json            # 项目依赖
├── vite.config.js          # Vite 配置
```

## 安装与运行
### 前端
1. 安装依赖：
   ```bash
   npm install
   ```
2. 启动开发服务器：
   ```bash
   npm run dev
   ```
3. 打开浏览器访问：`http://localhost:5173`

### 后端
1. 创建虚拟环境并安装依赖：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows 使用 venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. 启动 Flask 应用：
   ```bash
   python backend/app.py
   ```
3. 后端服务运行在：`http://127.0.0.1:5001`

## API 端点
- `POST /ai/nl2cypher`：自然语言到 Cypher 查询转换
- `POST /ai/rag`：智能 RAG 问答（流式响应）
- `GET /ai/schema`：获取知识图谱模式信息
- `POST /admin/cache/clear`：清除缓存
- `GET /health`：健康检查

## 贡献


## 许可证
