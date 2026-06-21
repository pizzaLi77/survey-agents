from app.schemas.callback import EvidenceItem
from app.schemas.medical_record import MedicalRecord, OcrResult


class EvidenceTool:
    def build(self, records: list[MedicalRecord], ocr_results: list[OcrResult]) -> list[EvidenceItem]:
        source = ocr_results[0] if ocr_results else None
        evidence_list: list[EvidenceItem] = []
        for record in records:
            evidence_text = record.evidence_text or (source.text if source else None)
            source_image_id = source.image_id if source else None
            evidence_list.extend(
                [
                    EvidenceItem(
                        field_name="hospital_name",
                        field_value=record.hospital_name,
                        evidence_text=evidence_text,
                        source_image_id=source_image_id,
                        confidence=0.9,
                    ),
                    EvidenceItem(
                        field_name="visit_date_start",
                        field_value=record.visit_date_start,
                        evidence_text=evidence_text,
                        source_image_id=source_image_id,
                        confidence=0.9,
                    ),
                    EvidenceItem(
                        field_name="diagnosis",
                        field_value=record.diagnosis,
                        evidence_text=evidence_text,
                        source_image_id=source_image_id,
                        confidence=0.9,
                    ),
                ]
            )
        return evidence_list
