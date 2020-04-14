import os
import sys
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
        self.log_level = kwargs.get("log_level", "info")
        self.sort_possibilities = ["size", "res"]
        self.known_image_extensions = ["jpg", "png"]
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

    def set_up_logger(self):
        n_level = getattr(logging, self.log_level.upper(), 20)
        if n_level == 20 and self.log_level.upper() != "INFO":
            sys.stdout.write("%s: %s\n" % ("Invalid log level", self.log_level))
        # Console logger
        formatter = logging.Formatter("%(name)s - %(levelname)s: %(message)s")
        self.logger = logging.getLogger("STPDF.Core")
        self.logger.setLevel(n_level)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(n_level)
        self.logger.addHandler(ch)
        msg = "%s: %s" % ("Core logger is set with log level", self.log_level)
        self.logger.info(msg)

    # Create directories to sort by size/res
    def create_sized_dirs(self):
        times = 1
        for i in range(10):
            dir_name = os.path.join(self.dest, self.difference * times)
            if not os.path.isdir(dir_name):
                os.mkdir(dir_name)
            times += 1

    # Gets number of files to sort
    def get_number_of_files(self):
        number_of_files = 0
        for dirpath, dirnames, filenames in os.walk(self.source):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if(os.path.isfile(fp)):
                    number_of_files += 1
        # self.logger.debug("Found %s files" % (number_of_files))
        return number_of_files

    # Main function for sorting
    def sort_all(self):
        # iterate trough all files in source
        for root, dirs, files in os.walk(self.source, topdown=False):
            for file in files:
                extension = os.path.splitext(file)[1][1:].lower()
                source_path = os.path.join(root, file)
                destination_dir = os.path.join(self.dest, extension)

                if not os.path.exists(destination_dir):
                    os.mkdir(destination_dir)
                if self.keep_filename:
                    file_name = file
                else:
                    file_name = "%s.%s" % (self.file_counter,extension)

                destination_file = os.path.join(destination_dir, file_name)
                if not os.path.exists(destination_file):
                    shutil.copy2(source_path, destination_file)

                # check and yield progress
                self.file_counter += 1
                if(round(self.file_counter % self.one_percent_files, 1) == 0.1):
                    self.logger.info(str(self.file_counter) + " / " + self.totalAmountToCopy + " processed.")
                    yield(str(self.file_counter) + " / " + self.totalAmountToCopy + " processed.\n")

        # this needs to be moved onto another function to avoid a high cyclomatic complexity
        final_dest = os.path.join(self.dest, "PROCESSED")
        self.logger.info("Sorting images in %s by date" % (final_dest))
        for img in self.postprocess_images(final_dest, self.min_evt_delta_days, self.split_months):
            print(img)

    # Iterates trough the processed image dir, processes each individual file
    # and yield the processed image
    def postprocess_images(self, image_dir, min_evt_delta_days, split_by_month):
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                extension = os.path.splitext(file)[1][1:].lower()
                if extension  in self.known_image_extensions:
                    yield self.postprocess_image(image_dir, file)
                else:
                    print("Skipping file %s, not an image" % file)

    def postprocess_image(self, image_directory, file_name):
        image_path = os.path.join(image_directory, file_name)
        image = open(image_path, 'rb')
        creation_time = None
        try:
            exifTags = exifread.process_file(image, details=False)
            creation_time = get_minimum_creation_time(exifTags)
        except Exception as e:
            # self.logger.warning("invalid exif tags for %s" % (file_name))
            # self.logger.debug("Exception: %s" % (str(e)))
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