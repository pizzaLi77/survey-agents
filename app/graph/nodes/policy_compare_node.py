from app.graph.nodes.base import AgentNode
from app.graph.state import AgentState
from app.tools.policy_tool import PolicyCompareTool


class PolicyCompareNode(AgentNode):
    name = "PolicyCompareNode"

    def __init__(self) -> None:
        self.policy_tool = PolicyCompareTool()

    async def execute(self, state: AgentState) -> AgentState:
        if not state.policy_info:
            state.status = "MANUAL_REVIEW"
            state.error_message = "保单信息不存在"
            return state
        for record in state.medical_records:
            record.before_or_after_policy = self.policy_tool.compare(
                record.visit_date_start,
                state.policy_info.effective_date,
            )
        return state

    def output_summary(self, state: AgentState) -> str:
        compared = [record.before_or_after_policy for record in state.medical_records]
        return f"policyCompare={compared}"
