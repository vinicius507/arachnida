from argparse import ArgumentParser, Namespace

from scorpion.image import Image


class ScorpionNamespace(Namespace):
    files: list[Image]


def parse_args() -> ScorpionNamespace:
    parser = ArgumentParser(
        prog="scorpion",
        description="Handle images metadata with ease.",
        epilog="École 42 project by vgoncalv.",
    )
    parser.add_argument("files", nargs="+", type=Image, help="Image files to handle.")
    return parser.parse_args(namespace=ScorpionNamespace())
