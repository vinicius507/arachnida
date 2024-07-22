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
    bold_green = "\033[1;32m"
    bold_yellow = "\033[1;33m"
    reset = "\033[0m"

    print(f"\n{bold_green}File:{reset} {metadata.file_name}")
    print(f"{bold_green}File size:{reset} {metadata.file_size} bytes")
    print(f"{bold_green}Create Time:{reset} {metadata.create_time}")

    if not metadata.exif_tags:
        print(f"{bold_yellow}No EXIF tags found{reset}")
        return
    print(bold_green + "EXIF tags:" + reset)
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
