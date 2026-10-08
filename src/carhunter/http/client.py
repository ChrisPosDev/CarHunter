import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import logging

logger = logging.getLogger(__name__)

class HttpClient:
    def __init__(self):
        # We use a single client for connection pooling and HTTP/2
        self._client = httpx.AsyncClient(
            http2=True,
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True
    )
    async def get(self, url: str) -> str:
        logger.debug(f"Fetching {url}")
        response = await self._client.get(url)
        response.raise_for_status()
        return response.text

    async def close(self):
        await self._client.aclose()

