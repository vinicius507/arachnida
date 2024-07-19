import asyncio
import html.parser
import logging
import urllib.parse
from argparse import ArgumentParser, Namespace
from collections.abc import Iterable

import httpx

logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class URL(str):
    def __new__(cls, url: str) -> "URL":
        if not urllib.parse.urlparse(url).scheme:
            raise ValueError(f"Invalid URL: {url}")
        return super().__new__(cls, url)

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return f"URL({super().__repr__()})"


class ImageParser(html.parser.HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.found_images = set()

    def handle_starttag(self, tag: str, attrs):
        if tag != "img":
            return
        for attr, value in attrs:
            if attr != "src":
                continue
            self.found_images.add(urllib.parse.urljoin(self.base_url, value))


class SpiderNamespace(Namespace):
    url: URL


class Spider:
    def __init__(
        self,
        client: httpx.AsyncClient,
        urls: Iterable[URL] = set(),
        max_workers=10,
    ) -> None:
        self.client = client

        self.urls = set(urls)
        self.seen: set[URL] = set()
        self.done: set[URL] = set()

        self.queue = asyncio.Queue()
        self.max_workers = max_workers

    async def run(self) -> None:
        new_urls = self.urls - self.seen
        self.seen.update(new_urls)

        for url in new_urls:
            await self.queue.put(url)

        workers = [asyncio.create_task(self.worker()) for _ in range(self.max_workers)]
        await self.queue.join()

        for worker in workers:
            worker.cancel()

    async def worker(self):
        while True:
            url = await self.queue.get()
            try:
                await self.crawl(url)
            except httpx.TimeoutException as e:
                logger.warning(f"Timeout crawling {url}: {e}")
            except httpx.HTTPError as e:
                logger.error(f"Error crawling {url}: {e}")
            except Exception as e:
                logger.exception(f"Error crawling {url}: {e}")
            finally:
                self.queue.task_done()

    async def crawl(self, url: URL) -> None:
        logger.info("Crawling URL: ", url)
        response = await self.client.get(url)
        parser = ImageParser(url)

        parser.feed(response.text)

        logger.info("Found images for %s: %s", url, parser.found_images)

        response.raise_for_status()
        self.done.add(url)


def parse_args() -> SpiderNamespace:
    parser = ArgumentParser(description="Extracts images from a given URL.")

    parser.add_argument(
        "urls", nargs="+", type=URL, help="The URL to extract images from"
    )
    return parser.parse_args(namespace=SpiderNamespace())


async def start() -> None:
    args = parse_args()
    clientOptions = {
        "follow_redirects": True,
        "limits": httpx.Limits(max_connections=10, max_keepalive_connections=10),
        "timeout": httpx.Timeout(3.0, connect=1.0),
    }

    async with httpx.AsyncClient(**clientOptions) as client:
        spider = Spider(client, urls=args.urls)
        await spider.run()


def main() -> None:
    asyncio.run(start())


if __name__ == "__main__":
    main()
