import asyncio
import logging
from pathlib import Path
from typing import Iterable

import httpx

from spider.parsers import ImageParser
from spider.url import URL

logger = logging.getLogger(__name__)


class Spider:
    def __init__(
        self,
        client: httpx.AsyncClient,
        data_dir: Path,
        extensions: Iterable[str],
        urls: Iterable[URL] = set(),
        max_workers=10,
    ) -> None:
        self.client = client
        self.data_dir = data_dir
        self.extensions = extensions
        self.urls = set(urls)
        self.seen: set[URL] = set()
        self.done: set[URL] = set()
        self.queue = asyncio.Queue()
        self.max_workers = max_workers

        self.data_dir.mkdir(parents=True, exist_ok=True)

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
        logger.info("Crawling URL: %s", url)
        res = await self.client.get(url)

        res.raise_for_status()
        found_images = self.parse_imgs(url, res.text)
        await asyncio.gather(*(self.download_image(src) for src in found_images))

        self.done.add(url)

    def parse_imgs(self, base_url: URL, text: str) -> set[str]:
        parser = ImageParser(base_url, self.extensions)
        parser.feed(text)
        return parser.found_images

    async def download_image(self, src: str):
        filename = src.split("/")[-1].split("?")[0].split("#")[0]
        filepath = f"{self.data_dir}/{filename}"

        logger.info("Downloading image: %s", src)
        res = await self.client.get(src)
        res.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(res.content)

        logger.info("Downloaded image: %s", src)
