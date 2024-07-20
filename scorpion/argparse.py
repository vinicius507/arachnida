from argparse import ArgumentParser, Namespace

from scorpion.image import Image


class ScorpionNamespace(Namespace):
    files: list[Image]


def parse_args() -> ScorpionNamespace:
    parser = ArgumentParser()
    parser.add_argument("files", nargs="+", type=Image)
    return parser.parse_args(namespace=ScorpionNamespace())
