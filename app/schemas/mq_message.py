from pydantic import BaseModel


class AgentTaskMessage(BaseModel):
    taskId: str
    surveyContentId: str | None = None
    websocketKey: str | None = None
    conclusionType: str | None = None
    bizType: str | None = "CLAIM"
    callbackUrl: str | None = None
    traceId: str | None = None
    createTime: str | None = None
