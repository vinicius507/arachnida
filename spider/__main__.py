import asyncio
import logging
import sys

import httpx

from spider.argparse import parse_args
from spider.spider import Spider

logging.basicConfig(
    format="%(asctime)s: %(levelname)5s: %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DEFAULT_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")


async def start() -> None:
    args = parse_args()
    clientOptions = {
        "follow_redirects": True,
        "limits": httpx.Limits(max_connections=10, max_keepalive_connections=10),
        "timeout": httpx.Timeout(3.0, connect=1.0),
    }
    data_dir = args.path.resolve()
    extensions = args.extensions.split(",") if args.extensions else DEFAULT_EXTENSIONS

    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error("Error creating data directory %s: %s", data_dir, e)
        sys.exit(1)

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
