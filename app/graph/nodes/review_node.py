from app.clients.llm_client import LlmClient
from app.graph.nodes.base import AgentNode
from app.graph.state import AgentState


class ReviewNode(AgentNode):
    name = "ReviewNode"

    def __init__(self) -> None:
        self.llm_client = LlmClient()

    async def execute(self, state: AgentState) -> AgentState:
        state.review_result = await self.llm_client.review(
            state.final_conclusion or "",
            state.medical_records,
            state.evidence_list,
        )
        if state.review_result.passed and state.review_result.score >= 80:
            state.status = "SUCCESS"
            return state
        if state.review_result.score < 60:
            state.status = "MANUAL_REVIEW"
            state.error_message = "Review Agent 质检不通过，转人工审核"
            return state
        state.status = "MANUAL_REVIEW"
        state.error_message = "Review Agent 质检分数偏低"
        return state

    def output_summary(self, state: AgentState) -> str:
        if not state.review_result:
            return "reviewResult=None"
        return f"passed={state.review_result.passed}, score={state.review_result.score}, status={state.status}"
