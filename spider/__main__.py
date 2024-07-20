import asyncio
import logging
import sys

import httpx

from spider.argparse import parse_args
from spider.log import ColoredFormatter
from spider.ratelimit import RateLimit
from spider.spider import Spider

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(ColoredFormatter())
logging.basicConfig(handlers=[handler], level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")


async def start() -> None:
    args = parse_args()
    data_dir = args.path.resolve()
    extensions = args.extensions.split(",") if args.extensions else DEFAULT_EXTENSIONS
    client = httpx.AsyncClient(
        follow_redirects=True,
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=10),
        timeout=httpx.Timeout(3.0, connect=1.0),
        transport=RateLimit(httpx.AsyncHTTPTransport(), 10),
    )

    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error("Error creating data directory %s: %s", data_dir, e)
        sys.exit(1)

    async with client:
        spider = Spider(
            client,
            data_dir=args.path,
            extensions=extensions,
            urls=args.urls,
            max_depth=args.limit,
            recursive=args.recursive,
        )
        await spider.run()


def main() -> None:
    asyncio.run(start())


if __name__ == "__main__":
    main()
