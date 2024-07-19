import asyncio

import httpx


class RateLimit(httpx.AsyncBaseTransport):
    def __init__(self, transport: httpx.AsyncBaseTransport, limit: int):
        super().__init__()
        self.transport = transport
        self.limit = limit
        self.semaphore = asyncio.Semaphore(limit)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        async with self.semaphore:
            await asyncio.sleep(0.3)
            return await self.transport.handle_async_request(request)
