from argparse import ArgumentParser, FileType, Namespace
from typing import BinaryIO


class ScorpionNamespace(Namespace):
    files: list[BinaryIO]


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("files", nargs="+", type=FileType("rb"))
    return parser.parse_args(namespace=ScorpionNamespace())
