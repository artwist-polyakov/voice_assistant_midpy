from db.models.requests.base_request import BaseRequest


class SearchRequest(BaseRequest):
    external_user_id: str
    external_session_id: str
    query: str
