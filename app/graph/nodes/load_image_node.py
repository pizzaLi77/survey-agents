from app.clients.java_client import JavaClient
from app.graph.nodes.base import AgentNode
from app.graph.state import AgentState


class LoadImageNode(AgentNode):
    name = "LoadImageNode"

    def __init__(self, java_client: JavaClient) -> None:
        self.java_client = java_client

    async def execute(self, state: AgentState) -> AgentState:
        state.image_list = await self.java_client.load_images(state.task_id)
        if not state.image_list:
            state.status = "MANUAL_REVIEW"
            state.error_message = "影像列表为空"
        return state

    def output_summary(self, state: AgentState) -> str:
        return f"imageCount={len(state.image_list)}, status={state.status}"
