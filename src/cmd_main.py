import sys
import argparse

from core.sorter import FileSorter
from core.custom_exceptions import OutDirNotEmpty, DirMissing, WhyWouldYou
from core.utils import verify_required


def parse_and_return_args():
    descript = (
        "Sort Images by date and remaining files by size or resolution\n"
        "The input files are first copied to the destination(can be skipped), sorted by file type.\n"
        "Then they are sorted based on creation year\n"
        "Finally any directories containing more than a maximum number of files are accordingly split into separate directories."
    )
    parser = argparse.ArgumentParser(description=descript)
    parser.add_argument("from_dir", help="Directory that holds the files")
    parser.add_argument("to_dir", help="Directory to store organized files")
    parser.add_argument("-sr", "--sort-remaining", help="Sort remaining files that could not be analyzed", action="store_true")
    parser.add_argument("-sb",
                        "--sort-by",
                        default="size",
                        help="Sort remaining files by size or resolution (size|res)")
    parser.add_argument("--difference",
                        nargs="?",
                        default=200,
                        type=int,
                        help="Used when sorting by size ")
    parser.add_argument("--keep-name",
                        action="store_true",
                        help="If this argument is passed the original filename is preserved")
    parser.add_argument("--skip-copy", help="Works with the original files instead of copying them", action="store_true")
    args = parser.parse_args()
    return args


def run_main():
    args = parse_and_return_args()
    msg = "Verifying paths before proceeding"
    sys.stdout.write(msg + "\n")
    try:
        verify_required(args)
    except (WhyWouldYou, OutDirNotEmpty, DirMissing) as e:
        raise e
    source = args.from_dir
    dest = args.to_dir
    kn = args.keep_name
    sk = args.skip_copy
    sr = args.sort_remaining
    sb = args.sort_by
    df = args.difference
    msg = "Initializing FileSorter"
    sys.stdout.write(msg + "\n")
    try:
        sorter = FileSorter(source,
                            dest,
                            diff=df,
                            keep_name=kn,
                            skip_copy=sk,
                            sort_unknown=(sr, sb))
        sys.stdout.write(sorter.return_all_options_string())
    except (WhyWouldYou, OutDirNotEmpty, DirMissing) as e:
        raise e


if __name__ == '__main__':
    try:
        run_main()
    except Exception as e:
        sys.stdout.write("\n" + str(e) + "\n")
        sys.exit(1)
