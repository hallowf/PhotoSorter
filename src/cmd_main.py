import argparse

from core.sorter import FileSorter


def parse_and_return_args():
    description = (
        "Sort files by date\n"
        "The input files are first copied to the destination, sorted by file type.\n"
        "Then they are sorted based on creation year\n"
        "Finally any directories containing more than a maximum number of files are accordingly split into separate directories."
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("from_dir", help="Directory that holds the files")
    parser.add_argument("to_dir", help="Directory to store organized files")
    parser.add_argument("--split_by", help="Split remaining files by size or resolution (size|res)")
    args = parser.parse_args()
    return args


def run_main():
    args = parse_and_return_args()




if __name__ == '__main__':
    run_main()
