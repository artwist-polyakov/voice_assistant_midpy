import aiohttp

session = aiohttp.ClientSession()

async def get_response(url: str, params: dict = None, method: str = 'GET', cookies: dict = None):
    """
    Функция отправляет асинхронный запрос на сервер
    и возвращает ответ
    """
    async with session as s:
        async with s.request(method=method.lower(), url=url, params=params) as response:
            body = await response.json()
            status = response.status
            return body, status
