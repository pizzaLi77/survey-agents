from pydantic import BaseModel


class ImageInfo(BaseModel):
    image_id: str
    image_url: str
    image_name: str | None = None


class OcrResult(BaseModel):
    image_id: str
    text: str
    confidence: float | None = None


class PolicyInfo(BaseModel):
    policy_no: str
    insured_name: str
    effective_date: str


class MedicalRecord(BaseModel):
    hospital_name: str | None = None
    visit_type: str | None = None
    visit_date_start: str | None = None
    visit_date_end: str | None = None
    department: str | None = None
    diagnosis: str | None = None
    chief_complaint: str | None = None
    present_illness: str | None = None
    past_history: str | None = None
    family_history: str | None = None
    before_or_after_policy: str | None = None
    evidence_text: str | None = None
