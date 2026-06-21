from fastapi import FastAPI

from app.graph.workflow import InvestigationConclusionWorkflow
from app.schemas.mq_message import AgentTaskMessage

app = FastAPI(title="Survey Agent Service")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "UP"}


@app.post("/debug/tasks/{task_id}/run")
async def run_task(task_id: str) -> dict[str, str]:
    message = AgentTaskMessage(taskId=task_id, surveyContentId="", traceId=f"debug-{task_id}")
    workflow = InvestigationConclusionWorkflow()
    state = await workflow.run(message)
    return {"taskId": state.task_id, "status": state.status}
