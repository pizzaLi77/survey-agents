from abc import ABC, abstractmethod

from app.graph.state import AgentState


class AgentNode(ABC):
    name: str
    report_trace: bool = True

    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        raise NotImplementedError

    def input_summary(self, state: AgentState) -> str:
        return f"taskId={state.task_id}"

    def output_summary(self, state: AgentState) -> str:
        return f"status={state.status}"
