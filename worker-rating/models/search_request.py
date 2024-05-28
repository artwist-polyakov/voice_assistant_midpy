from models.base_request import BaseRequest


class SearchRequest(BaseRequest):
    external_user_id: str
    external_session_id: str
    external_message_id: str
    query: str
