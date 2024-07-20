import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import filetype
import httpx

from spider.parsers import AnchorParser, ImageParser
from spider.url import URL

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CrawlURL(tuple[URL, int]):
    url: URL
    depth: int = 0

    def __new__(cls, url: URL, depth: int = 1):
        return super().__new__(cls, (url, depth))

    def __str__(self):
        return self.url


class Spider:
    def __init__(
        self,
        client: httpx.AsyncClient,
        data_dir: Path,
        extensions: Iterable[str],
        urls: Iterable[URL] = set(),
        max_depth: int = 5,
        max_workers: int = 10,
        recursive: bool = False,
    ) -> None:
        self.client = client
        self.data_dir = data_dir
        self.extensions = extensions
        self.urls: set[CrawlURL] = set(map(CrawlURL, urls))
        self.seen: set[CrawlURL] = set()
        self.done: set[CrawlURL] = set()
        self.queue: asyncio.Queue[CrawlURL] = asyncio.Queue()
        self.max_depth = max_depth
        self.max_workers = max_workers
        self.recursive = recursive

        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def run(self) -> None:
        await self.on_found_links(self.urls)
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
                logger.warning("Timeout crawling %s: %s", url, e)
            except Exception as e:
                logger.exception("Error crawling %s: %s", url, e)
            finally:
                self.queue.task_done()

    async def crawl(self, crawl_url: CrawlURL) -> None:
        logger.debug("Crawling URL: %s", crawl_url)
        res = await self.client.get(crawl_url.url)
        url, depth = crawl_url

        if self.recursive and depth < self.max_depth:
            found_links = {
                CrawlURL(link, depth + 1)
                for link in self.parse_links(url, res.text)
                if link not in self.done
            }
            await self.on_found_links(found_links)

        res.raise_for_status()
        found_images = self.parse_images(url, res.text)
        await asyncio.gather(*(self.download_image(url, src) for src in found_images))

        self.done.add(crawl_url)

    def parse_links(self, base_url: URL, text: str) -> set[URL]:
        parser = AnchorParser(base_url)
        parser.feed(text)
        return parser.found_links

    async def on_found_links(self, links: set[CrawlURL]) -> None:
        new_links = links - self.seen
        self.seen.update(new_links)

        for link in new_links:
            if urlparse(link.url).scheme not in ("http", "https"):
                continue
            await self.queue.put(link)

    def parse_images(self, base_url: URL, text: str) -> set[str]:
        parser = ImageParser(base_url)
        parser.feed(text)
        return parser.found_images

    async def download_image(self, url: URL, src: str):
        logger.info("Downloading image: %s", src)
        res = await self.client.get(src)
        res.raise_for_status()

        kind = filetype.guess(res.content)

        if kind is None:
            logger.error("Could not determine image filetype: %s", src)
            return

        if kind.extension not in self.extensions:
            logger.warning("Unregistered image extension: %s", kind.extension)
            return

        filename = urlparse(src).path.split("/")[-1].split(".")[0]
        filename = filename + "_" + datetime.today().strftime("%Y%m%d-%H%M%S")
        filename = f"{filename}.{kind.extension}"
        if hostname := urlparse(url).hostname:
            filename = f"{hostname}_{filename}"

        with Path(self.data_dir, filename).open(mode="wb") as f:
            f.write(res.content)

        logger.info("Downloaded image: %s", src)
