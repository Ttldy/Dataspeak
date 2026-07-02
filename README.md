# DataSpeak 智能问数 Agent

DataSpeak 是一个面向企业私域结构化数据的智能问数 Agent。用户输入自然语言后，系统通过 LangGraph 状态机自动完成意图路由、Schema 检索、结构化 Plan、SQL 生成、只读执行、结果校验、错误回溯修正和最终数据分析输出。

## 核心功能

- LangGraph Agent Workflow：将 Router、Schema Retrieval、Plan、SQL Generation、SQL Execution、Validation、Repair 和 QA/Fallback 封装为可观测节点。
- 动态路由：区分数据库查询、结果追问、数据问答和闲聊。
- 字段级 Schema 三级索引：关键词索引、向量索引、Rerank 索引。
- 混合检索：关键词召回 + 向量召回 + RRF 融合 + 精排。
- 结构化 Plan：输出可审计 JSON 步骤，不暴露隐藏推理链。
- SQL 安全：仅允许 SELECT，禁用写操作，自动 LIMIT，限制表字段来源。
- 工具层：`execute_sql`、`inspect_schema`、`explain_sql`、`get_last_result`。
- 回溯修正：Schema、Plan、SQL、执行四类错误最多 3 轮自动重跑。
- 记忆：短期滑动窗口 + 摘要压缩，长期记忆默认只存摘要和偏好。
- Demo：FastAPI + Streamlit + 示例业务数据 + Benchmark。

## 技术栈

FastAPI、Streamlit、LangGraph、LangChain Core、SQLite/MySQL、Redis、Milvus、Python、Pydantic、Docker Compose、BM25-like 检索、RRF、规则 fallback、Ollama/OpenAI-compatible 适配器。

## 本地运行

```powershell
git clone https://github.com/Ttldy/Dataspeak.git
cd DataSpeak
conda activate ds
pip install -r requirements.txt
python scripts/init_demo_data.py
python scripts/build_schema_index.py
uvicorn dataspeak.app.main:app --host 127.0.0.1 --port 18088
streamlit run dataspeak_web/app.py --server.port 18501
```

API 文档：`http://127.0.0.1:18088/docs`

前端 Demo：`http://127.0.0.1:18501`

### Windows 一键启动

```powershell
cd DataSpeak
conda activate ds
powershell -ExecutionPolicy Bypass -File scripts/start_dataspeak.ps1
```

在项目根目录执行该脚本。脚本会检查项目目录和 conda 环境，必要时从 `.env.example` 复制 `.env`，使用 `docker compose -p dataspeak up -d` 启动 DataSpeak 专属 Docker 服务，初始化 demo 数据、构建 Schema 索引，并在两个新的 PowerShell 窗口中分别启动 FastAPI 与 Streamlit。

### Windows 一键关闭

```powershell
cd DataSpeak
powershell -ExecutionPolicy Bypass -File scripts/stop_dataspeak.ps1
```

脚本只按端口 `18501`、`18088` 和 Docker Compose project `dataspeak` 定位资源，停止 Streamlit、FastAPI 与 DataSpeak Docker 服务，不会删除容器、卷或影响 EnterpriseMind。

## 测试与评测

```powershell
pytest -q
python scripts/smoke_test.py
python -m dataspeak.evaluation.benchmark
```

### Windows 一键测试

```powershell
cd DataSpeak
conda activate ds
powershell -ExecutionPolicy Bypass -File scripts/test_dataspeak.ps1
```

测试脚本只在 `ds` 环境中运行 `pytest -q`、`python scripts/smoke_test.py` 和 `python -m dataspeak.evaluation.benchmark`，不会启动、停止或删除 Docker 容器。
