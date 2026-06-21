from datetime import date


class PolicyCompareTool:
    def compare(self, visit_date: str | None, effective_date: str | None) -> str | None:
        if not visit_date or not effective_date:
            return None
        visit = date.fromisoformat(visit_date)
        effective = date.fromisoformat(effective_date)
        return "投保前" if visit < effective else "投保后"
