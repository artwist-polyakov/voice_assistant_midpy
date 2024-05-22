from db.models.responses.base_response import BaseResponse


class SearchResponse(BaseResponse):
    data: dict
