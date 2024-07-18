from argparse import ArgumentParser, Namespace
from urllib.parse import urlparse


class URL(str):
    def __new__(cls, url: str) -> "URL":
        if not urlparse(url).scheme:
            raise ValueError(f"Invalid URL: {url}")
        return super().__new__(cls, url)

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return f"URL({super().__repr__()})"


class SpiderNamespace(Namespace):
    url: URL


def main() -> None:
    parser = ArgumentParser(description="Extracts images from a given URL.")

    parser.add_argument("url", type=URL, help="The URL to extract images from")
    args = parser.parse_args(None, SpiderNamespace())

    print(args)


if __name__ == "__main__":
    main()
