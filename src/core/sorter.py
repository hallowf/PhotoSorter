import os
import shutil
import exifread
import ntpath
import logging
from datetime import datetime
from time import localtime, mktime, strftime, strptime
from .custom_exceptions import DirMissing, OutDirNotEmpty, WhyWouldYou
from .image_data import get_image_resolution, get_image_size, get_minimum_creation_time


class FileSorter(object):
    """docstring for FileSorter."""

    def __init__(self, source, dest, **kwargs):
        super(FileSorter, self).__init__()
        # File sorting parameters
        self.dest = os.path.abspath(dest)
        self.source = os.path.abspath(source)
        self.dest_items = None
        self.difference = kwargs.get("diff", 200)
        self.keep_filename = kwargs.get("keep_name", False)
        self.skip_copy = kwargs.get("skip_copy", False)
        self.sort_possibilities = ["size", "res"]
        sort_remaining, sort_remaining_by = kwargs.get("sort_unknown", (True, "size"))
        self.sort_remaining = sort_remaining
        # check if sorting parameters are correct and default them if not
        if sort_remaining is True and sort_remaining_by not in self.sort_possibilities:
            self.sort_remaining_by = "size"
        else:
            self.sort_remaining_by = sort_remaining_by
        self.f_map = None
        self.min_evt_delta_days = 4
        self.maxNumberOfFilesPerFolder = 500
        self.split_months = False
        self.file_number = self.get_number_of_files()
        self.one_percent_files = self.file_number/100
        self.totalAmountToCopy = str(self.file_number)
        self.file_counter = 0

    # Gets number of files to sort
    def get_number_of_files(self):
        number_of_files = 0
        for dirpath, dirnames, filenames in os.walk(self.source):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if(os.path.isfile(fp)):
                    number_of_files += 1
        self.logger.debug("Found %s files" % (number_of_files))
        return number_of_files