import os
from .custom_exceptions import DirMissing, WhyWouldYou, OutDirNotEmpty


def verify_required(args):
    if not os.path.isdir(args.from_dir):
        raise DirMissing("Specified source directory does not exist")
    elif len(os.listdir(args.from_dir)) == 0:
        raise WhyWouldYou("There are not enough files to process")
    elif len(os.listdir(args.to_dir)) > 0:
        raise OutDirNotEmpty("Specified destination directory isn't empty")
