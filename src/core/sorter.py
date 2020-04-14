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
        self.file_counter = 0
        self.create_sized_dirs()

    # Create directories to sort by size
    def create_sized_dirs(self):
        times = 1
        for i in range(10):
            dir_name = os.path.join(self.dest, self.difference * times)
            os.mkdir(dir_name)
            times = times + 1

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

    def postprocess_image(self, image_directory, file_name):
        image_path = os.path.join(image_directory, file_name)
        image = open(image_path, 'rb')
        creation_time = None
        try:
            exifTags = exifread.process_file(image, details=False)
            creation_time = get_minimum_creation_time(exifTags)
        except Exception as e:
            self.logger.warning("invalid exif tags for %s" % (file_name))
            self.logger.debug("Exception: %s" % (str(e)))
            yield "invalid exif tags for %s\n" % (file_name)

        # distinct different time types
        if creation_time is None:
            creation_time = localtime(os.path.getctime(image_path))
        else:
            try:
                creation_time = strptime(str(creation_time), "%Y:%m:%d %H:%M:%S")
            except Exception as e:
                # self.logger.debug("Exception: %s" % (str(e)))
                creation_time = localtime(os.path.getctime(image_path))
        return (mktime(creation_time), image_path)
        image.close()