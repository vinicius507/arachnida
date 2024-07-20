from dataclasses import dataclass
from io import BufferedReader
from pathlib import Path
from typing import Any

import exifread

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")


class Image:
    def __init__(self, path: str):
        if (ext := Path(path).suffix) not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {ext}")

        self.file_path = Path(path).resolve(strict=True)

    def open(self) -> BufferedReader:
        return self.file_path.open("rb")

    def __str__(self) -> str:
        return self.file_path.name

    def __repr__(self) -> str:
        return f"Image({self.file_path.name})"


@dataclass(frozen=True)
class ImageMetadata:
    file_name: str
    file_size: int
    exif_tags: dict[str, Any]

    @classmethod
    def from_image(cls, image: Image) -> "ImageMetadata":
        with image.open() as data:
            exif_tags = exifread.process_file(data)

        return cls(
            file_name=image.file_path.name,
            file_size=image.file_path.stat().st_size,
            exif_tags=exif_tags,
        )
