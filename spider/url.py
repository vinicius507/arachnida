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
