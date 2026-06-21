from app.graph.nodes.base import AgentNode
from app.graph.state import AgentState
from app.tools.ocr_tool import OcrTool


class OcrNode(AgentNode):
    name = "OcrNode"

    def __init__(self) -> None:
        self.ocr_tool = OcrTool()

    async def execute(self, state: AgentState) -> AgentState:
        state.ocr_results = await self.ocr_tool.recognize(state.image_list)
        texts = [result.text for result in state.ocr_results if result.text.strip()]
        if not texts:
            state.status = "MANUAL_REVIEW"
            state.error_message = "OCR 无有效文本"
            return state
        state.merged_ocr_text = "\n".join(texts)
        return state

    def input_summary(self, state: AgentState) -> str:
        return f"imageCount={len(state.image_list)}"

    def output_summary(self, state: AgentState) -> str:
        text_len = len(state.merged_ocr_text or "")
        return f"ocrCount={len(state.ocr_results)}, mergedTextLength={text_len}"
