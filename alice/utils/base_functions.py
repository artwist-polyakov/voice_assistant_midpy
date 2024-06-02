import aiohttp


async def get_response(session: aiohttp.ClientSession, url: str, params: dict = None, method: str = 'GET', cookies: dict = None):
    async with session.request(method=method.lower(), url=url, params=params, cookies=cookies) as response:
        body = await response.json()
        status = response.status
        return body, status
