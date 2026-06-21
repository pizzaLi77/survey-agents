from app.clients.java_client import JavaClient
from app.graph.nodes.base import AgentNode
from app.graph.state import AgentState


class CallbackNode(AgentNode):
    name = "CallbackNode"
    report_trace = False

    def __init__(self, java_client: JavaClient) -> None:
        self.java_client = java_client

    async def execute(self, state: AgentState) -> AgentState:
        await self.java_client.callback(state)
        return state

    def input_summary(self, state: AgentState) -> str:
        return f"status={state.status}, taskId={state.task_id}"
