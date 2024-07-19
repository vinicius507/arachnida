from argparse import ArgumentParser, Namespace
from pathlib import Path

from spider.url import URL


class SpiderNamespace(Namespace):
    data_dir: Path
    extensions: str
    urls: list[URL]


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
