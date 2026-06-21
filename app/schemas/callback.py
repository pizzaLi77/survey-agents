from pydantic import BaseModel, Field

from app.schemas.medical_record import MedicalRecord


class EvidenceItem(BaseModel):
    field_name: str
    field_value: str | None = None
    evidence_text: str | None = None
    source_image_id: str | None = None
    confidence: float | None = None


class ReviewResult(BaseModel):
    passed: bool
    score: int
    problems: list[str] = Field(default_factory=list)
    suggestion: str | None = None


class AgentCallbackRequest(BaseModel):
    taskId: str
    status: str
    finalConclusion: str | None = None
    medicalRecords: list[MedicalRecord] = Field(default_factory=list)
    evidenceList: list[EvidenceItem] = Field(default_factory=list)
    reviewResult: ReviewResult | None = None
    errorMessage: str | None = None
