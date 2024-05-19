from typing import Any

from pydantic import BaseModel


class Meta(BaseModel):
    locale: str
    timezone: str
    client_id: str
    interfaces: dict[str, Any]


class User(BaseModel):
    user_id: str


class Application(BaseModel):
    application_id: str


class Session(BaseModel):
    message_id: int
    session_id: str
    skill_id: str
    user: User
    application: Application
    new: bool
    user_id: str


class NLU(BaseModel):
    tokens: list
    entities: list
    intents: dict


class RequestModel(BaseModel):
    command: str
    original_utterance: str
    nlu: NLU
    markup: dict[str, bool]
    type: str


class RequestBody(BaseModel):
    meta: Meta
    session: Session
    request: RequestModel
    version: str
