import os
import sys
import argparse

from core.sorter import FileSorter
from core.custom_exceptions import OutDirNotEmpty, DirMissing, WhyWouldYou


def parse_and_return_args():
    description = (
        "Sort files by date\n"
        "The input files are first copied to the destination(can be skipped), sorted by file type.\n"
        "Then they are sorted based on creation year\n"
        "Finally any directories containing more than a maximum number of files are accordingly split into separate directories."
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("from_dir", help="Directory that holds the files")
    parser.add_argument("to_dir", help="Directory to store organized files")
    parser.add_argument("--sort-remaining", help="Sort remaining files that could not be analyzed", action="store_true")
    parser.add_argument("--sort-by", help="Sort remaining files by size or resolution (size|res)")
    parser.add_argument("--difference", help="Used when sorting by size ")
    parser.add_argument("--skip-copy", help="Works with the original files instead of copying them", action="store_true")
    args = parser.parse_args()
    return args


def verify_required(args):
    if not os.path.isdir(args.from_dir):
        raise DirMissing("Specified source directory does not exist")
    elif len(os.listdir(args.from_dir)) <= 0:
        raise WhyWouldYou("There are not enough files to process")
    elif len(os.listdir(args.to_dir)) > 0:
        raise OutDirNotEmpty("Specified destination directory isn't empty")


def run_main():
    args = parse_and_return_args()
    try:
        verify_required(args)
    except (WhyWouldYou, OutDirNotEmpty, DirMissing) as e:
        raise e
    source = args.from_dir
    dest = args.to_dir
    sk = args.skip_copy
    sr = args.sort_remaining
    sb = args.sort_by
    try:
        sorter = FileSorter(source,
                            dest,
                            skip_copy=sk,
                            sort_unknown=(sr, sb))
    except (WhyWouldYou, OutDirNotEmpty, DirMissing) as e:
        raise e


if __name__ == '__main__':
    try:
        run_main()
    except Exception as e:
        sys.stdout.write("\n" + str(e) + "\n")
