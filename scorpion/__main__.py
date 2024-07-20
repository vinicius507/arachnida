import logging
import sys

from scorpion.argparse import parse_args
from scorpion.image import ImageMetadata
from scorpion.log import ColoredFormatter

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(ColoredFormatter())
logging.basicConfig(handlers=[handler], level=logging.INFO)
logger = logging.getLogger(__name__)


def report_metadata(metadata: ImageMetadata):
    print(f"File: {metadata.file_name}")
    print(f"File size: {metadata.file_size} bytes")

    if not metadata.exif_tags:
        return
    print("EXIF tags:")
    for tag, value in metadata.exif_tags.items():
        print(f"  {tag}: {value}")


def main():
    args = parse_args()
    images_metadata: list[ImageMetadata] = list()

    for image in args.files:
        logging.info("Processing file: %s", image)

        try:
            metadata = ImageMetadata.from_image(image)
            images_metadata.append(metadata)
        except ValueError as e:
            logging.error(e)

    for metadata in images_metadata:
        report_metadata(metadata)


if __name__ == "__main__":
    main()
