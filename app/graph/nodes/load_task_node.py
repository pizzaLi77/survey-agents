from app.clients.java_client import JavaClient
from app.graph.nodes.base import AgentNode
from app.graph.state import AgentState


class LoadTaskNode(AgentNode):
    name = "LoadTaskNode"

    def __init__(self, java_client: JavaClient) -> None:
        self.java_client = java_client

    async def execute(self, state: AgentState) -> AgentState:
        data = await self.java_client.load_task_context(state.task_id)
        if data.get("status") == "CANCELED":
            state.status = "CANCELED"
            state.error_message = "任务已取消"
            return state
        await self.java_client.mark_running(state.task_id)
        state.status = "RUNNING"
        state.survey_content_id = data.get("surveyContentId")
        state.insured_name = data.get("insuredName")
        state.policy_info = self.java_client.parse_policy_info(data)
        return state

    def output_summary(self, state: AgentState) -> str:
        return f"status={state.status}, surveyContentId={state.survey_content_id}"
