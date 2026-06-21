from app.schemas.callback import ReviewResult
from app.schemas.medical_record import MedicalRecord


class LlmClient:
    async def extract_medical_records(self, ocr_text: str) -> list[MedicalRecord]:
        return [
            MedicalRecord(
                hospital_name="南京市第一人民医院",
                visit_type="住院",
                visit_date_start="2024-05-20",
                visit_date_end="2024-05-25",
                department="心内科",
                diagnosis="冠心病",
                chief_complaint="胸闷3天",
                present_illness="活动后胸闷",
                past_history="高血压5年",
                family_history="无特殊",
                evidence_text=ocr_text[:500],
            )
        ]

    async def generate_conclusion(self, insured_name: str | None, records: list[MedicalRecord]) -> str:
        parts: list[str] = []
        name = insured_name or "被投保人"
        for record in records:
            parts.append(
                "经核查："
                f"{record.hospital_name}，被投保人存在1次{record.visit_type}记录："
                f"{record.visit_date_start}至{record.visit_date_end}，{name}因{record.chief_complaint}"
                f"在{record.department}{record.visit_type}，诊断为{record.diagnosis}，"
                f"现病史记载{record.present_illness}；既往史/家族史："
                f"{record.past_history or '无特殊'}/{record.family_history or '无特殊'}。"
                f"本次就诊记录在{record.before_or_after_policy}。"
            )
        return "\n".join(parts)

    async def review(self, conclusion: str, records: list[MedicalRecord]) -> ReviewResult:
        problems: list[str] = []
        for record in records:
            for value in [record.hospital_name, record.visit_date_start, record.diagnosis, record.before_or_after_policy]:
                if value and value not in conclusion:
                    problems.append(f"结论缺少字段：{value}")
        return ReviewResult(
            passed=not problems,
            score=92 if not problems else 65,
            problems=problems,
            suggestion=None if not problems else "请根据结构化病例重新生成结论",
        )
