import time

from app.clients.java_client import JavaClient
from app.graph.nodes.base import AgentNode
from app.graph.nodes.callback_node import CallbackNode
from app.graph.nodes.conclusion_generate_node import ConclusionGenerateNode
from app.graph.nodes.evidence_build_node import EvidenceBuildNode
from app.graph.nodes.load_image_node import LoadImageNode
from app.graph.nodes.load_task_node import LoadTaskNode
from app.graph.nodes.medical_extract_node import MedicalExtractNode
from app.graph.nodes.ocr_node import OcrNode
from app.graph.nodes.policy_compare_node import PolicyCompareNode
from app.graph.nodes.review_node import ReviewNode
from app.graph.state import AgentState
from app.schemas.mq_message import AgentTaskMessage


class InvestigationConclusionWorkflow:
    def __init__(self) -> None:
        self.java_client = JavaClient()
        self.nodes: list[AgentNode] = [
            LoadTaskNode(self.java_client),
            LoadImageNode(self.java_client),
            OcrNode(),
            MedicalExtractNode(),
            PolicyCompareNode(),
            EvidenceBuildNode(),
            ConclusionGenerateNode(),
            ReviewNode(),
            CallbackNode(self.java_client),
        ]

    async def run(self, message: AgentTaskMessage) -> AgentState:
        state = AgentState(
            task_id=message.taskId,
            survey_content_id=message.surveyContentId,
            websocket_key=message.websocketKey,
            conclusion_type=message.conclusionType,
            trace_id=message.traceId,
        )
        for node in self.nodes:
            started = time.perf_counter()
            try:
                state = await node.execute(state)
                cost_time_ms = int((time.perf_counter() - started) * 1000)
                if node.report_trace:
                    await self.java_client.record_step(
                        state.task_id,
                        node.name,
                        "SUCCESS",
                        node.input_summary(state),
                        node.output_summary(state),
                        cost_time_ms,
                        state.retry_count,
                        None,
                    )
            except Exception as exc:
                state.status = "FAILED"
                state.error_message = str(exc)
                cost_time_ms = int((time.perf_counter() - started) * 1000)
                await self.java_client.record_step(
                    state.task_id,
                    node.name,
                    "FAILED",
                    node.input_summary(state),
                    "",
                    cost_time_ms,
                    state.retry_count,
                    state.error_message,
                )
                await CallbackNode(self.java_client).execute(state)
                break
            if state.status in {"FAILED", "MANUAL_REVIEW", "CANCELED"}:
                if node.name != "CallbackNode":
                    await CallbackNode(self.java_client).execute(state)
                break
        return state
