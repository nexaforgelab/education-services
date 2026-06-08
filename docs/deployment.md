# Education Services — 部署指南

## 一、环境要求

| 组件 | 最低 | 推荐 |
|---|---|---|
| CPU | 2 核 | 4 核+ |
| 内存 | 4 GB | 8 GB+ |
| 存储 | 20 GB | 100 GB+ |
| Python | 3.11 | 3.11+ |
| Docker | 24+ | 最新 |
| PostgreSQL | 15+ | 16+ |
| pgvector | 0.5+ | 最新 |

## 二、本地开发

### 1. 克隆代码

```bash
git clone https://github.com/your-org/education-services.git
cd education-services
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入真实 API key 等
```

`.env` 示例：
```bash
# LLM
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://education:education@localhost:5432/education_services

# MinIO / S3
S3_ENDPOINT=localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=education-services

# MCP
TEXTBOOK_MCP_URL=http://localhost:8001
VECTOR_INDEX_MCP_URL=http://localhost:8002
STUDENT_PROFILE_MCP_URL=http://localhost:8003
HOMEWORK_STORE_MCP_URL=http://localhost:8004
QUESTION_BANK_MCP_URL=http://localhost:8005

# App
ENV=development
LOG_LEVEL=INFO
```

### 3. 启动依赖

```bash
docker compose up -d postgres minio
```

### 4. 安装 Python 依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt --break-system-packages
```

### 5. 初始化数据库

```bash
# 应用 schema
psql -h localhost -U education -d education_services -f migrations/001_initial.sql
```

### 6. 启动后端

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. 验证

```bash
# 健康检查
curl http://localhost:8000/health

# 登录
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "role": "teacher"}' | jq -r .access_token)

# 列出教材
curl http://localhost:8000/api/v1/textbooks -H "Authorization: Bearer $TOKEN"
```

## 三、Docker Compose 部署

```bash
# 启动所有服务
docker compose up -d

# 查看日志
docker compose logs -f backend

# 停止
docker compose down
```

## 四、生产部署

### 1. Kubernetes

```bash
# 1. 创建命名空间
kubectl create namespace education-services

# 2. 创建 Secret（API key）
kubectl create secret generic api-secrets \
  --from-literal=anthropic-api-key=$ANTHROPIC_API_KEY \
  -n education-services

# 3. 应用配置
kubectl apply -f k8s/configmap.yaml

# 4. 部署 PostgreSQL（用云数据库或自托管）
kubectl apply -f k8s/postgres.yaml

# 5. 部署后端
kubectl apply -f k8s/backend.yaml

# 6. 部署 ingress
kubectl apply -f k8s/ingress.yaml
```

### 2. 云服务

#### AWS

```
- ECS Fargate (后端容器)
- RDS for PostgreSQL + pgvector
- S3 (文件存储)
- CloudFront (CDN)
- Route 53 (DNS)
- ALB (负载均衡)
```

#### Azure

```
- AKS (Kubernetes)
- Azure Database for PostgreSQL
- Blob Storage
- Front Door
```

#### GCP

```
- Cloud Run (后端)
- Cloud SQL for PostgreSQL
- Cloud Storage
- Cloud CDN
```

## 五、扩容

### 单机

| 指标 | 阈值 | 行动 |
|---|---|---|
| CPU > 80% | 持续 5 min | 升级到 4 核 |
| 内存 > 80% | 持续 5 min | 升级到 8 GB |
| 响应时间 > 30s | 持续 1 min | 排查 + 升级 |

### 集群

```bash
# 后端扩容
kubectl scale deployment backend --replicas=10

# 数据库扩容
# 升级 RDS instance class / 增加 read replica
```

## 六、备份与恢复

### PostgreSQL 备份

```bash
# 每日备份
pg_dump -h localhost -U education education_services > backup_$(date +%Y%m%d).sql

# 上传到 S3
aws s3 cp backup_*.sql s3://education-services-backups/
```

### MinIO / S3 备份

```bash
# 镜像到另一个 bucket
mc mirror source/bucket dest/bucket
```

### 恢复

```bash
# 恢复 PostgreSQL
psql -h localhost -U education education_services < backup_20260607.sql
```

## 七、监控

### Prometheus + Grafana

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

### 关键指标

| 指标 | 阈值 |
|---|---|
| request_count | - |
| latency_p99 | < 60s |
| error_rate | < 5% |
| citation_count_per_response | ≥ 1 |
| safety_flag_count | 0 |

## 八、安全

### HTTPS

```bash
# Let's Encrypt
certbot certonly --standalone -d api.education-services.com
```

### WAF

- Cloudflare WAF
- AWS WAF

### 限流

- nginx rate limit
- Cloudflare rate limit

## 九、CI/CD

### GitHub Actions

`.github/workflows/deploy.yml`：
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build & push
        run: |
          docker build -t registry/education-services:${{ github.sha }} ./backend
          docker push registry/education-services:${{ github.sha }}
      - name: Deploy
        run: kubectl set image deployment/backend backend=registry/education-services:${{ github.sha }}
```

## 十、故障排查

### 启动失败

```bash
# 查看日志
docker compose logs backend

# 进入容器
docker compose exec backend bash
```

### 数据库连接失败

```bash
# 测试连接
psql -h localhost -U education -d education_services

# 检查 service
docker compose ps
```

### LLM 调用失败

```bash
# 测试 API key
curl -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/messages
```

## 十一、升级

```bash
# 1. 备份
./scripts/backup.sh

# 2. 拉取新代码
git pull

# 3. 运行数据库迁移
psql -f migrations/002_xxx.sql

# 4. 重新构建镜像
docker compose build

# 5. 重启服务
docker compose up -d
```

## 十二、回滚

```bash
# 1. 恢复数据库
psql -f backup_20260607.sql

# 2. 回滚镜像
docker compose down
git checkout v0.1.0
docker compose up -d
```
