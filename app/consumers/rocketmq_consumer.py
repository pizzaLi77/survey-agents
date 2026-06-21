from app.graph.workflow import InvestigationConclusionWorkflow
from app.schemas.mq_message import AgentTaskMessage


class RocketMqConsumer:
    async def consume(self, payload: dict) -> str:
        message = AgentTaskMessage(**payload)
        state = await InvestigationConclusionWorkflow().run(message)
        return state.status
