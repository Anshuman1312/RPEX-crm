from pydantic import BaseModel


class AIAskRequest(BaseModel):
    question: str
