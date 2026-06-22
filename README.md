# Survey Agents

理赔调查结论生成 Agent Demo。

当前实现按设计文档先跑通本地主流程：

1. Java 服务创建任务并暴露内部接口。
2. Python Agent 通过 `taskId` 加载上下文和影像列表。
3. Workflow 使用 mock OCR，并在配置模型密钥后调用 LLM 完成结构化抽取、结论生成和 Review 质检。
4. Python Agent 回调 Java 保存最终状态。

LLM 配置：

```bash
set LLM_API_KEY=sk-xxx
set LLM_BASE_URL=https://api.deepseek.com
set LLM_MODEL=deepseek-chat
```

未配置 `LLM_API_KEY` 时，服务会使用本地规则兜底，方便离线跑通 demo；配置后会调用 OpenAI 兼容的 `/chat/completions` 接口，并用 Pydantic 校验结构化 JSON 输出。

启动：

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

手动触发：

```bash
curl -X POST http://127.0.0.1:8001/debug/tasks/{taskId}/run
```
