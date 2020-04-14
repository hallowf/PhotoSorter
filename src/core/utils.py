import os
from .custom_exceptions import DirMissing, WhyWouldYou, OutDirNotEmpty


def verify_required(args):
    if not os.path.isdir(args.from_dir):
        raise DirMissing("Specified source directory does not exist")
    elif verify_dir_subfolders(args.from_dir) == False:
        raise WhyWouldYou("There are not enough files to process")
    elif len(os.listdir(args.to_dir)) > 0:
        raise OutDirNotEmpty("Specified destination directory isn't empty")

# verify if there are items in possible subfolders
# returns true or false
def verify_dir_subfolders(directory):
    num_of_items = os.listdir(directory)
    if len(num_of_items) == 1:
        # change directory to subfolder and recurse
        if os.path.isdir(os.path.join(directory, num_of_items[0])):
            return verify_dir_subfolders(os.path.join(directory, num_of_items[0]))
        else:
            # just one item no need to process
            return False
    elif len(num_of_items) > 1:
        # ideally this should check each subfolder
        # but it might hit recursion limit
        # so for now it returns true
        return True
    else:
        # no items to process
        return False