import html.parser
from typing import Iterable
from urllib.parse import urljoin, urlparse


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
            image_path = str(urlparse(value).path.lower())
            if image_path.endswith(self.extensions):
                self.found_images.add(urljoin(self.base_url, value))