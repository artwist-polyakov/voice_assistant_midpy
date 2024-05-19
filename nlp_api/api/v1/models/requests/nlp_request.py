from enum import Enum

from pydantic import BaseModel, Field


class AssistantType(str, Enum):
    ALICE = "alice"


class QuestionParam(BaseModel):
    text: str = Field(
        ...,
        description="Question text"
    )
    assistant: AssistantType = Field(
        AssistantType.ALICE,
        description="Assistant type"
    )
