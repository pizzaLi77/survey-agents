from app.clients.llm_client import LlmClient
from app.graph.nodes.base import AgentNode
from app.graph.state import AgentState


class MedicalExtractNode(AgentNode):
    name = "MedicalExtractNode"

    def __init__(self) -> None:
        self.llm_client = LlmClient()

    async def execute(self, state: AgentState) -> AgentState:
        if not state.merged_ocr_text:
            state.status = "MANUAL_REVIEW"
            state.error_message = "缺少 OCR 文本"
            return state
        state.medical_records = await self.llm_client.extract_medical_records(state.merged_ocr_text)
        if not state.medical_records:
            state.status = "MANUAL_REVIEW"
            state.error_message = "未抽取到病例记录"
        return state

    def output_summary(self, state: AgentState) -> str:
        return f"recordCount={len(state.medical_records)}, status={state.status}"
