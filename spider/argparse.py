from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path

from spider.url import URL


class SpiderNamespace(Namespace):
    data_dir: Path
    extensions: str
    urls: list[URL]
    recursive: bool
    limit: int


def parse_args() -> SpiderNamespace:
    parser = ArgumentParser(
        prog="spider",
        description="Extracts images from a given URL.",
        epilog="École 42 project by vgoncalv.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

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
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively searches URLs for images",
    )
    parser.add_argument(
        "-l",
        "--limit",
        default=5,
        type=int,
        help="The maximum depth level of the recursive image search",
    )
    return parser.parse_args(namespace=SpiderNamespace())
