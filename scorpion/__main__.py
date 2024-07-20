import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

import exifread

from scorpion.argparse import parse_args
from scorpion.log import ColoredFormatter

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(ColoredFormatter())
logging.basicConfig(handlers=[handler], level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MetaData:
    file_name: str
    file_size: int
    exif_tags: dict[str, Any]


SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")


def parse_metadata(file: BinaryIO) -> MetaData:
    exif_tags = exifread.process_file(file)

    return MetaData(
        file_name=file.name,
        file_size=file.seek(0, os.SEEK_END),
        exif_tags=exif_tags,
    )


def main():
    args = parse_args()

    for file in args.files:
        file_name = Path(file.name).resolve(strict=True)
        logging.info("Processing file: %s", file_name)
        extname = file_name.suffix

        if extname not in SUPPORTED_EXTENSIONS:
            logging.warning("Unsupported file extension: %s", extname)
            continue

        metadata = parse_metadata(file)
        logging.info("Image metadata: %s", metadata)
        file.close()


if __name__ == "__main__":
    main()
