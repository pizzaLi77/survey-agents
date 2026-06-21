import httpx

from app.config import settings
from app.graph.state import AgentState
from app.schemas.medical_record import ImageInfo, PolicyInfo


class JavaClient:
    def __init__(self) -> None:
        self.base_url = settings.java_base_url.rstrip("/")
        self.timeout = settings.request_timeout_seconds

    async def mark_running(self, task_id: str) -> None:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            await client.post(f"{self.base_url}/internal/agent/tasks/{task_id}/running")

    async def load_task_context(self, task_id: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/internal/agent/tasks/{task_id}/context")
            response.raise_for_status()
            return response.json()

    async def load_images(self, task_id: str) -> list[ImageInfo]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/internal/agent/tasks/{task_id}/images")
            response.raise_for_status()
            data = response.json()
        return [
            ImageInfo(
                image_id=item["imageId"],
                image_name=item.get("imageName"),
                image_url=item["imageUrl"],
            )
            for item in data.get("images", [])
        ]

    async def record_step(
        self,
        task_id: str,
        step_name: str,
        status: str,
        input_summary: str,
        output_summary: str,
        cost_time_ms: int,
        retry_count: int,
        error_message: str | None,
    ) -> None:
        payload = {
            "stepName": step_name,
            "status": status,
            "inputSummary": input_summary,
            "outputSummary": output_summary,
            "costTimeMs": cost_time_ms,
            "retryCount": retry_count,
            "errorMessage": error_message,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/internal/agent/tasks/{task_id}/steps", json=payload)
            response.raise_for_status()

    async def callback(self, state: AgentState) -> None:
        payload = self._build_callback_payload(state)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/internal/agent/tasks/{state.task_id}/callback",
                json=payload,
            )
            response.raise_for_status()

    @staticmethod
    def parse_policy_info(data: dict) -> PolicyInfo | None:
        policy = data.get("policyInfo")
        if not policy:
            return None
        return PolicyInfo(
            policy_no=policy["policyNo"],
            insured_name=policy["insuredName"],
            effective_date=policy["effectiveDate"],
        )

    @staticmethod
    def _build_callback_payload(state: AgentState) -> dict:
        return {
            "taskId": state.task_id,
            "status": state.status,
            "finalConclusion": state.final_conclusion,
            "medicalRecords": [
                {
                    "hospitalName": record.hospital_name,
                    "visitType": record.visit_type,
                    "visitDateStart": record.visit_date_start,
                    "visitDateEnd": record.visit_date_end,
                    "department": record.department,
                    "diagnosis": record.diagnosis,
                    "chiefComplaint": record.chief_complaint,
                    "presentIllness": record.present_illness,
                    "pastHistory": record.past_history,
                    "familyHistory": record.family_history,
                    "beforeOrAfterPolicy": record.before_or_after_policy,
                    "evidenceText": record.evidence_text,
                }
                for record in state.medical_records
            ],
            "evidenceList": [
                {
                    "fieldName": item.field_name,
                    "fieldValue": item.field_value,
                    "evidenceText": item.evidence_text,
                    "sourceImageId": item.source_image_id,
                    "confidence": item.confidence,
                }
                for item in state.evidence_list
            ],
            "reviewResult": None
            if state.review_result is None
            else {
                "passed": state.review_result.passed,
                "score": state.review_result.score,
                "problems": state.review_result.problems,
                "suggestion": state.review_result.suggestion,
            },
            "errorMessage": state.error_message,
        }
