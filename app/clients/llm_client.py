import json
import re
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.config import settings
from app.prompts.conclusion_generate_prompt import CONCLUSION_GENERATE_PROMPT
from app.prompts.medical_extract_prompt import MEDICAL_EXTRACT_PROMPT
from app.prompts.review_prompt import REVIEW_PROMPT
from app.schemas.callback import EvidenceItem, ReviewResult
from app.schemas.medical_record import MedicalRecord


class MedicalExtractResponse(BaseModel):
    records: list[MedicalRecord] = Field(default_factory=list)


class LlmClient:
    def __init__(self) -> None:
        self.base_url = settings.llm_base_url.rstrip("/")
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.timeout = settings.request_timeout_seconds
        self.temperature = settings.llm_temperature
        self.max_retries = max(settings.llm_max_retries, 1)

    async def extract_medical_records(self, ocr_text: str) -> list[MedicalRecord]:
        if not self.api_key:
            return self._fallback_extract_medical_records(ocr_text)

        content = await self._chat(
            MEDICAL_EXTRACT_PROMPT,
            "OCR文本：\n" + ocr_text,
            response_format={"type": "json_object"},
        )
        data = self._loads_json_object(content)
        return MedicalExtractResponse.model_validate(data).records

    async def generate_conclusion(
        self,
        insured_name: str | None,
        records: list[MedicalRecord],
        evidence_list: list[EvidenceItem],
    ) -> str:
        if not self.api_key:
            return self._fallback_generate_conclusion(insured_name, records)

        payload = {
            "insured_name": insured_name,
            "records": [record.model_dump() for record in records],
            "evidence_list": [item.model_dump() for item in evidence_list],
        }
        return await self._chat(
            CONCLUSION_GENERATE_PROMPT,
            "请根据以下结构化病例和证据链生成调查结论：\n"
            + json.dumps(payload, ensure_ascii=False),
        )

    async def review(
        self,
        conclusion: str,
        records: list[MedicalRecord],
        evidence_list: list[EvidenceItem],
    ) -> ReviewResult:
        if not self.api_key:
            return self._fallback_review(conclusion, records, evidence_list)

        payload = {
            "conclusion": conclusion,
            "records": [record.model_dump() for record in records],
            "evidence_list": [item.model_dump() for item in evidence_list],
        }
        content = await self._chat(
            REVIEW_PROMPT,
            "请质检以下调查结论：\n" + json.dumps(payload, ensure_ascii=False),
            response_format={"type": "json_object"},
        )
        data = self._loads_json_object(content)
        return ReviewResult.model_validate(data)

    async def _chat(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, str] | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
        }
        if response_format:
            payload["response_format"] = response_format

        headers = {"Authorization": f"Bearer {self.api_key}"}
        last_error: Exception | None = None
        for _ in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
            except Exception as exc:
                last_error = exc
        raise RuntimeError(f"LLM调用失败: {last_error}") from last_error

    @staticmethod
    def _loads_json_object(content: str) -> dict[str, Any]:
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text).strip()
            text = re.sub(r"```$", "", text).strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                raise
            data = json.loads(match.group(0))
        if not isinstance(data, dict):
            raise ValueError("LLM JSON输出必须是对象")
        return data

    @staticmethod
    def _fallback_extract_medical_records(ocr_text: str) -> list[MedicalRecord]:
        def first(pattern: str) -> str | None:
            match = re.search(pattern, ocr_text)
            return match.group(1).strip() if match else None

        hospital_name = first(r"([\u4e00-\u9fa5A-Za-z0-9]+医院)")
        visit_date_start = first(r"(\d{4}-\d{2}-\d{2})")
        visit_date_end = first(r"至(\d{4}-\d{2}-\d{2})")
        diagnosis = first(r"诊断为([^。，\n]+)")
        chief_complaint = first(r"主诉([^。，\n]+)")
        present_illness = first(r"现病史记载([^。，\n]+)")
        past_history = first(r"既往史([^。，\n]+)")
        department = first(r"在([^。，\n]*科)")
        visit_type = "住院" if "住院" in ocr_text else "门诊" if "门诊" in ocr_text else None

        if not any([hospital_name, visit_date_start, diagnosis]):
            return []
        return [
            MedicalRecord(
                hospital_name=hospital_name,
                visit_type=visit_type,
                visit_date_start=visit_date_start,
                visit_date_end=visit_date_end,
                department=department,
                diagnosis=diagnosis,
                chief_complaint=chief_complaint,
                present_illness=present_illness,
                past_history=past_history,
                evidence_text=ocr_text[:500],
            )
        ]

    @staticmethod
    def _fallback_generate_conclusion(insured_name: str | None, records: list[MedicalRecord]) -> str:
        name = insured_name or "被投保人"
        parts: list[str] = []
        for record in records:
            parts.append(
                "经核查："
                f"{record.hospital_name or '未知医院'}，"
                f"{name}存在1次{record.visit_type or '就诊'}记录："
                f"{record.visit_date_start or '时间不详'}"
                f"{'至' + record.visit_date_end if record.visit_date_end else ''}，"
                f"{name}因{record.chief_complaint or '症状不详'}"
                f"在{record.department or '未知科室'}{record.visit_type or '就诊'}，"
                f"诊断为{record.diagnosis or '诊断不详'}，"
                f"现病史记载{record.present_illness or '无明确记载'}；"
                f"既往史/家族史：{record.past_history or '无特殊'}/"
                f"{record.family_history or '无特殊'}。"
                f"本次就诊记录在{record.before_or_after_policy or '投保时间关系不明'}。"
            )
        return "\n".join(parts)

    @staticmethod
    def _fallback_review(
        conclusion: str,
        records: list[MedicalRecord],
        evidence_list: list[EvidenceItem],
    ) -> ReviewResult:
        problems: list[str] = []
        evidence_text = "\n".join(item.evidence_text or "" for item in evidence_list)
        for record in records:
            for field_name, value in [
                ("hospital_name", record.hospital_name),
                ("visit_date_start", record.visit_date_start),
                ("diagnosis", record.diagnosis),
                ("before_or_after_policy", record.before_or_after_policy),
            ]:
                if value and value not in conclusion:
                    problems.append(f"结论缺少字段 {field_name}: {value}")
                if value and field_name != "before_or_after_policy" and value not in evidence_text:
                    problems.append(f"证据链缺少字段 {field_name}: {value}")

        score = max(100 - len(problems) * 10, 0)
        return ReviewResult(
            passed=score >= 80,
            score=score,
            problems=problems,
            suggestion=None if score >= 80 else "请根据结构化病例和证据链重新生成结论",
        )
