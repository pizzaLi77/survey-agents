from pydantic import BaseModel, Field

from app.schemas.callback import EvidenceItem, ReviewResult
from app.schemas.medical_record import ImageInfo, MedicalRecord, OcrResult, PolicyInfo


class AgentState(BaseModel):
    task_id: str
    survey_content_id: str | None = None
    websocket_key: str | None = None
    conclusion_type: str | None = None
    trace_id: str | None = None
    image_list: list[ImageInfo] = Field(default_factory=list)
    ocr_results: list[OcrResult] = Field(default_factory=list)
    merged_ocr_text: str | None = None
    policy_info: PolicyInfo | None = None
    insured_name: str | None = None
    medical_records: list[MedicalRecord] = Field(default_factory=list)
    evidence_list: list[EvidenceItem] = Field(default_factory=list)
    draft_conclusion: str | None = None
    final_conclusion: str | None = None
    review_result: ReviewResult | None = None
    retry_count: int = 0
    status: str = "INIT"
    error_message: str | None = None
