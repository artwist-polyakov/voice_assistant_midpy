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


class FilmResponse(BaseModel):
    result: str
    name: str
    rating: float
    description: str
    id: int
    actors_names: list
    directors_names: list
    genres: list


class ErrorResponse(BaseModel):
    result: str


class SuccessResponse(BaseModel):
    result: str