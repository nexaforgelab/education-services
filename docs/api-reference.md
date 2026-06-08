# Education Services — API 参考

> 完整的 REST API、WebSocket、SSE 接口文档。

## 一、Base URL

```
http://localhost:8000/api/v1
```

## 二、认证

所有需要鉴权的接口需要 `Authorization: Bearer <token>` header。

### POST /auth/login

**请求：**
```json
{
  "user_id": "user_001",
  "role": "teacher",
  "name": "张老师"
}
```

**响应：**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "user_id": "user_001",
    "role": "teacher",
    "name": "张老师"
  },
  "expires_in": 86400
}
```

### POST /auth/refresh

刷新 token。

### GET /auth/me

获取当前用户信息。

**响应：**
```json
{
  "user_id": "user_001",
  "role": "teacher",
  "name": "张老师"
}
```

## 三、教材

### POST /textbooks/ingest

解析教材 PDF。

**请求：**
```json
{
  "pdf_path": "./samples/math_g7_pep.pdf",
  "subject": "math",
  "grade": "7",
  "version": "人教版"
}
```

**响应：**
```json
{
  "textbook_id": "math_g7_vol1_pep_2024",
  "title": "数学 七年级 上册",
  "total_pages": 156,
  "chapters_count": 6,
  "manifest_url": "./out/textbook_manifest.json"
}
```

### GET /textbooks

列出已入库教材。

**Query：** `?subject=math&grade=7`

### GET /textbooks/{textbook_id}/manifest

获取教材 manifest。

### GET /textbooks/{textbook_id}/chapters/{chapter_id}/content

获取章节内容。

## 四、Agent 调用

### POST /agents/lesson-plan

生成教案。

**请求：**
```json
{
  "textbook_id": "math_g7_vol1_pep_2024",
  "chapter_id": "ch01_s05",
  "duration_min": 45,
  "student_level": "中等"
}
```

**响应：**
```json
{
  "output_id": "uuid",
  "output_dir": "./out/uuid",
  "files": [
    "lesson_plan.md",
    "board_design.md",
    "question_chain.md",
    ...
  ],
  "citations_count": 5
}
```

### POST /agents/diagnose-homework

诊断作业。

**请求：**
```json
{
  "student_id": "stu_001",
  "textbook_id": "math_g7_vol1_pep_2024",
  "chapter_id": "ch01_s05",
  "homework_file_url": "https://...",
  "parsed_questions": [
    {
      "id": "q01",
      "student_answer": "0",
      "correct_answer": "2"
    }
  ]
}
```

### POST /agents/explain-to-parent

家长版解释。

### POST /agents/parent-report

家长报告。

### POST /agents/worksheet

生成分层练习。

### POST /agents/unit-review

单元复习。

## 五、流式响应（SSE）

### POST /agents/stream/lesson-plan

流式生成教案（Server-Sent Events）。

**请求：**
```json
{
  "textbook_id": "math_g7_vol1_pep_2024",
  "chapter_id": "ch01_s05",
  "duration_min": 45,
  "student_level": "中等"
}
```

**响应（SSE 格式）：**
```
data: {"stage": "start", "message": "开始生成教案..."}

data: {"stage": "locate", "message": "正在定位章节..."}

data: {"chunk": "##"}

data: {"chunk": "教"}

data: {"chunk": "学"}

...

data: {"stage": "complete"}

data: [DONE]
```

**前端使用：**
```javascript
const eventSource = new EventSource('/api/v1/agents/stream/lesson-plan', {
  method: 'POST',
  body: JSON.stringify({...})
});

eventSource.onmessage = (event) => {
  if (event.data === '[DONE]') {
    eventSource.close();
  } else {
    const data = JSON.parse(event.data);
    if (data.chunk) {
      // 追加到 UI
    } else if (data.stage) {
      // 显示阶段
    }
  }
};
```

### POST /agents/stream/diagnose-homework

流式诊断。

## 六、WebSocket

### WS /ws/{client_id}

建立 WebSocket 连接。

**消息格式：**
```json
{
  "type": "command" | "subscribe" | "feedback" | "ping",
  "payload": {...}
}
```

**示例：**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/client_001');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'command',
    payload: {
      command: '/lesson-plan',
      args: ['有理数加减法', '45', '中等']
    }
  }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log(msg);
  // 处理 progress / result / ...
};
```

## 七、错误码

| 状态码 | 含义 |
|---|---|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 / token 无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用（依赖缺失） |

## 八、限流

| 接口 | 限流 |
|---|---|
| /auth/* | 100 req/min/IP |
| /textbooks/ingest | 5 req/hour/IP |
| /agents/* | 20 req/min/user |
| /agents/stream/* | 5 concurrent/user |
| /ws/* | 10 concurrent/IP |

## 九、安全

### 数据脱敏

- 学生姓名 → alias
- 作业图片 → hash
- 错误日志 → 脱敏

### 审计日志

所有 Agent 输出都记录：
- 时间戳
- 用户 ID（hash）
- 输入 hash
- 输出引用数
- 未标依据数
- 安全触发数

## 十、SDK

### Python

```python
import requests

# 登录
token = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'user_id': 'user_001',
    'role': 'teacher'
}).json()['access_token']

# 调用 Agent
response = requests.post(
    'http://localhost:8000/api/v1/agents/lesson-plan',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'textbook_id': 'math_g7_vol1_pep_2024',
        'chapter_id': 'ch01_s05',
        'duration_min': 45,
        'student_level': '中等'
    }
)
print(response.json())
```

### JavaScript

```javascript
// 登录
const loginRes = await fetch('/api/v1/auth/login', {
  method: 'POST',
  body: JSON.stringify({ user_id: 'user_001', role: 'teacher' })
});
const { access_token } = await loginRes.json();

// 调用 Agent
const res = await fetch('/api/v1/agents/lesson-plan', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({...})
});
```

## 十一、变更日志

- v0.1.0：初版 API
- v0.2.0：增加流式响应 + WebSocket
- v0.3.0：增加认证和限流
