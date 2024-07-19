import asyncio
import html.parser
import logging
from argparse import ArgumentParser, Namespace
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DEFAULT_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")


class URL(str):
    def __new__(cls, url: str) -> "URL":
        if not urlparse(url).scheme:
            raise ValueError(f"Invalid URL: {url}")
        return super().__new__(cls, url)

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return f"URL({super().__repr__()})"


class ImageParser(html.parser.HTMLParser):
    def __init__(self, base_url: str, extensions: Iterable[str]) -> None:
        super().__init__()
        self.base_url = base_url
        self.extensions = tuple(extensions)
        self.found_images: set[str] = set()

    def handle_starttag(self, tag: str, attrs):
        if tag != "img":
            return
        for attr, value in attrs:
            if attr != "src":
                continue
            if urlparse(value).path.lower().endswith(self.extensions):
                self.found_images.add(urljoin(self.base_url, value))


class SpiderNamespace(Namespace):
    data_dir: Path
    extensions: str
    urls: list[URL]


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
        self.data_dir = data_dir.resolve()
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


def parse_args() -> SpiderNamespace:
    parser = ArgumentParser(description="Extracts images from a given URL.")

    parser.add_argument(
        "urls",
        nargs="+",
        type=URL,
        help="The URL to extract images from",
    )
    parser.add_argument(
        "-e",
        "--extensions",
        type=str,
        help="Comma separated list of image extensions to download",
    )
    parser.add_argument(
        "-p",
        "--path",
        default="./data",
        type=Path,
        help="The path to save the images",
    )
    return parser.parse_args(namespace=SpiderNamespace())


async def start() -> None:
    args = parse_args()
    clientOptions = {
        "follow_redirects": True,
        "limits": httpx.Limits(max_connections=10, max_keepalive_connections=10),
        "timeout": httpx.Timeout(3.0, connect=1.0),
    }
    extensions = args.extensions.split(",") if args.extensions else DEFAULT_EXTENSIONS

    async with httpx.AsyncClient(**clientOptions) as client:
        spider = Spider(
            client,
            extensions=extensions,
            urls=args.urls,
            data_dir=args.path,
        )
        await spider.run()


def main() -> None:
    asyncio.run(start())


if __name__ == "__main__":
    main()
