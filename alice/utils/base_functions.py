import aiohttp


async def get_response(url: str, params: dict = None, method: str = 'GET', cookies: dict = None):
    """
    Функция отправляет асинхронный запрос на сервер
    и возвращает ответ
    """
    async with aiohttp.ClientSession(cookies=cookies if cookies else None) as session:
        async with session.request(method=method.lower(), url=url, params=params) as response:
            body = await response.json()
            status = response.status
            return body, status
