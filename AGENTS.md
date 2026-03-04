# AGENTS.md - 项目开发指南

本文档为自动化编码代理提供项目开发规范和操作指南。

## 项目概述

小说合并工具，将TXT/Markdown章节文件合并生成EPUB电子书。
- **前端**: Vue 3 + Element Plus + Vite
- **后端**: FastAPI (Python) + pypandoc

---

## 1. 构建与运行命令

### 前端 (frontend/)

```bash
# 安装依赖
cd frontend && npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

### 后端 (backend/)

```bash
# 安装依赖
cd backend && pip install -r requirements.txt

# 开发模式
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker 部署

```bash
# 构建并启动容器
docker compose up -d

# 查看日志
docker compose logs -f

# 停止容器
docker compose down
```

### 测试命令

> 注意：当前项目尚未配置单元测试。

```bash
# 前端测试 (如配置)
npm run test

# 后端测试 (如配置)
pytest
```

---

## 2. 代码风格指南

### 2.1 通用规范

- **语言**: 所有代码注释和文档使用中文
- **缩进**: 4个空格
- **行长度**: 不超过120字符

### 2.2 Python (后端)

#### 导入规范
```python
# 标准库
import os
import sys

# 第三方库
from fastapi import FastAPI, UploadFile
from pathlib import Path

# 本地模块
from core.converter import convert_to_epub
```

#### 命名规范
- 变量/函数: `snake_case` (如 `book_title`)
- 类名: `PascalCase` (如 `BookGenerator`)
- 常量: `UPPER_SNAKE_CASE`

#### 类型注解
```python
def process_file(file_path: Path, content: str) -> bool:
    """处理文件并返回是否成功"""
    result: bool = True
    return result
```

#### 错误处理
```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"值错误: {e}")
    raise
except Exception as e:
    logger.error(f"未知错误: {e}")
    return None
```

### 2.3 Vue/JavaScript (前端)

#### 导入规范
```javascript
// Vue 组件和生命周期
import { ref, reactive, onMounted } from 'vue'

// 第三方库
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 本地组件
import FileUploader from './components/FileUploader.vue'
```

#### 命名规范
- 组件文件: `PascalCase` (如 `BookCard.vue`)
- 变量/函数: `camelCase` (如 `handleUpload`)

#### Vue 组件规范
```vue
<template>
  <div class="component-name">
    <!-- 模板内容 -->
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: String,
  count: { type: Number, default: 0 }
})

const emit = defineEmits(['update'])

const localData = ref(null)

onMounted(() => {
  // 初始化逻辑
})
</script>

<style scoped>
.component-name {
  /* 组件样式 */
}
</style>
```

---

## 3. 项目结构

```
novel-merger/
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── App.vue          # 主应用组件
│   │   └── main.js          # 入口文件
│   ├── package.json
│   └── vite.config.js
│
├── backend/                  # FastAPI 后端
│   ├── main.py              # 主应用入口
│   ├── core/                # 核心模块
│   │   ├── converter.py     # EPUB 转换
│   │   ├── cover_generator.py
│   │   ├── file_handler.py
│   │   └── text_processor.py
│   └── requirements.txt
│
├── docker-compose.yml
└── test_data/               # 测试数据
```

---

## 4. API 接口规范

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/merge | 合并并生成EPUB |
| POST | /api/preview | 预览合并结果 |

### 请求格式 (FormData)
- `files`: 文件列表 (.txt, .md)
- `book_title`: 书名
- `author`: 作者
- `order`: 文件顺序 (可选)
- `generate_cover`: 是否生成封面 (默认 true)

---

## 5. 开发注意事项

1. **LSP错误**: 容器内开发时本地报LSP错误正常，忽略即可
2. **跨域**: 前端通过 Vite 代理访问后端，路径为 `/api/*`
3. **容器网络**: Docker中前端访问后端应使用容器名 `novel-backend:8000`
4. **临时文件**: 后端使用 `tempfile` 处理上传文件，请求结束后自动清理

---

## 6. 常用调试命令

```bash
# 查看后端日志
docker compose logs backend -f

# 重启容器
docker compose restart

# 进入容器调试
docker exec -it novel-backend sh

# 测试API
curl -X POST http://localhost:8000/api/preview -F "files=@test.txt"
```
