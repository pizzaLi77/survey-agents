from app.graph.nodes.base import AgentNode
from app.graph.state import AgentState
from app.tools.evidence_tool import EvidenceTool


class EvidenceBuildNode(AgentNode):
    name = "EvidenceBuildNode"

    def __init__(self) -> None:
        self.evidence_tool = EvidenceTool()

    async def execute(self, state: AgentState) -> AgentState:
        state.evidence_list = self.evidence_tool.build(state.medical_records, state.ocr_results)
        return state

    def output_summary(self, state: AgentState) -> str:
        return f"evidenceCount={len(state.evidence_list)}"
