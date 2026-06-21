from app.clients.llm_client import LlmClient
from app.graph.nodes.base import AgentNode
from app.graph.state import AgentState


class ConclusionGenerateNode(AgentNode):
    name = "ConclusionGenerateNode"

    def __init__(self) -> None:
        self.llm_client = LlmClient()

    async def execute(self, state: AgentState) -> AgentState:
        state.draft_conclusion = await self.llm_client.generate_conclusion(state.insured_name, state.medical_records)
        state.final_conclusion = state.draft_conclusion
        return state

    def output_summary(self, state: AgentState) -> str:
        return f"conclusionLength={len(state.final_conclusion or '')}"
