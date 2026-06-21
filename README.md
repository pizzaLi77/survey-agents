# Survey Agents

理赔调查结论生成 Agent Demo。

当前实现按设计文档先跑通本地主流程：

1. Java 服务创建任务并暴露内部接口。
2. Python Agent 通过 `taskId` 加载上下文和影像列表。
3. Workflow 使用 mock OCR 和规则版 LLM 生成结构化病例、证据链、结论和 Review 结果。
4. Python Agent 回调 Java 保存最终状态。

启动：

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

手动触发：

```bash
curl -X POST http://127.0.0.1:8001/debug/tasks/{taskId}/run
```
