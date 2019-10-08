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
        self.skip_copy = kwargs.get("skip_copy", False)
        self.sort_possibilities = ["size", "res"]
        sort_unknown, sort_unknown_by = kwargs.get("sort_unknown", (True, "size"))
        # check if sorting parameters are correct and default them if not
        if sort_unknown is True and sort_unknown_by not in self.sort_possibilities:
            self.sort_unknown_by = "size"
        self.f_map = None
        self.min_evt_delta_days = 4
        self.maxNumberOfFilesPerFolder = 500
        self.split_months = False
        self.keep_filename = False
        # set up logging
        log_format = "%(name)s - %(level)s: %(message)s"
        logging.basicConfig(format=log_format)
        self.logger = logging.getLogger("PhotoSorter")
        # Check requirements and create sized dirs
        try:
            self.check_location()
        except (WhyWouldYou, DirMissing, OutDirNotEmpty) as e:
            raise e
        self.sized_dirs = []
        times = 1
        for i in range(10):
            self.sized_dirs.append(self.difference * times)
            times = times+1
        # File info
        self.file_number = self.get_number_of_files(source)
        self.one_percent_files = self.file_number/100
        self.totalAmountToCopy = str(self.file_number)
        self.file_counter = 0

    def check_location(self, skip_some=False):
        if not skip_some:
            self.logger.debug("Checking source and destination before starting")
            if not os.path.isdir(self.source):
                raise DirMissing("Source folder does not exist")
            if not os.path.isdir(self.dest):
                os.mkdir(self.dest)
        self.logger.debug("Listing folders and sub-folders")
        self.loc_items = os.listdir(self.source)
        print(len(self.loc_items))
        if len(self.loc_items) == 1:
            if os.path.isdir(os.path.join(self.source, self.loc_items[0])):
                self.source = os.path.abspath(os.path.join(self.source, self.loc_items[0]))
                print(self.source)
                self.check_location(skip_some=True)
        elif len(self.loc_items) == 0:
            raise WhyWouldYou("There are too few files to process...")
        self.dest_items = os.listdir(self.dest)
        if len(self.dest_items) >= 1:
            raise OutDirNotEmpty("Output directory is not empty")

    # Returns number of files from start dir
    def get_number_of_files(self, start_path='.'):
        self.logger.debug("Checking number of files to sort")
        number_of_files = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if(os.path.isfile(fp)):
                    number_of_files += 1
        self.logger.debug("Found %s files" % (number_of_files))
        return number_of_files

    # Main function for sorting
    def sort_all(self):
        # iterate trough all files in source
        for root, dirs, files in os.walk(self.source, topdown=False):
            for file in files:
                extension = os.path.splitext(file)[1][1:].upper()
                source_path = os.path.join(root, file)
                destination_dir = os.path.join(self.dest, extension)

                if not os.path.exists(destination_dir):
                    os.mkdir(destination_dir)
                if self.keep_filename:
                    file_name = file
                else:
                    file_name = str(self.file_counter) + "." + extension.lower()

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
        self.postprocess_images(final_dest, self.min_evt_delta_days, self.split_months)
        if self.sort_unknown:
            self.logger.info("Sorting unknown files by %s" % (self.sort_unknown_by))
            yield "Sorting unknown files by %s\n" % (self.sort_unknown_by)
            map_func = self.map_by_size if self.sort_unknown_by == "size" else self.map_by_res
            map_func(final_dest)
        yield "Done\n"

    # Iterates trough the processed image dir, processes each individual file
    # and passes the images to write_images
    def postprocess_images(self, image_dir, min_evt_delta_days, split_by_month):
        images = []
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                self.postprocess_image(images, image_dir, file)

        self.write_images(images, image_dir, min_evt_delta_days, split_by_month)

    def postprocess_image(self, images, image_directory, file_name):
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
                self.logger.debug("Exception: %s" % (str(e)))
                creation_time = localtime(os.path.getctime(image_path))
        images.append((mktime(creation_time), image_path))
        image.close()

    def write_images(self, images, dest_root, min_evt_delta_days, split_by_month=False):
        min_evt_delta = min_evt_delta_days * 60 * 60 * 24  # convert in seconds
        sorted_images = sorted(images)
        previous_time = None
        evt_number = 0
        previous_dest = None
        c_time = datetime.now()
        today = c_time.strftime("%d/%m/%Y")

        for img_tuple in sorted_images:
            dest = ""
            dest_file_path = ""
            t = localtime(img_tuple[0])
            year = strftime("%Y", t)
            month = split_by_month and strftime("%m", t) or None
            creation_date = strftime("%d/%m/%Y", t)
            file_name = ntpath.basename(img_tuple[1])

            if(creation_date == today):
                if self.sort_unknown:
                    dest = os.path.join(dest_root, "unknown-to-sort")
                    if not os.path.isdir(dest):
                        os.mkdir(dest)
                    dest_file_path = os.path.join(dest, file_name)
                else:
                    self.create_unknown_date_folder(dest_root)
                    dest = os.path.join(dest_root, "unknown")
                    dest_file_path = os.path.join(dest, file_name)
            else:
                self.logger.debug("%s was created in %s" % (file_name, creation_date))
                if (previous_time is None) or ((previous_time + min_evt_delta) < img_tuple[0]):
                    evt_number = evt_number + 1
                    self.create_new_folder(dest_root, year, month, evt_number)

                previous_time = img_tuple[0]

                dest_components = [dest_root, year, month, str(evt_number)]
                dest_components = [v for v in dest_components if v is not None]
                dest = os.path.join(*dest_components)

                # it may be possible that an event covers 2 years.
                # in such a case put all the images to the event in the old year
                if not (os.path.exists(dest)):
                    dest = previous_dest
                    # dest = os.path.join(dest_root, str(int(year) - 1), str(evt_number))

                previous_dest = dest
                dest_file_path = os.path.join(dest, file_name)

            if not (os.path.exists(dest_file_path)):
                shutil.move(img_tuple[1], dest)
            else:
                if (os.path.exists(img_tuple[1])):
                    os.remove(img_tuple[1])

    def create_unknown_date_folder(self, dest_root):
        path = os.path.join(dest_root, "unknown")
        if not os.path.exists(path):
            os.makedirs(path)

    def create_new_folder(self, dest_root, year, month, evt_number):
        if month is not None:
            new_path = os.path.join(dest_root, year, month, str(evt_number))
        else:
            new_path = os.path.join(dest_root, year, str(evt_number))
        if not os.path.exists(new_path):
            os.makedirs(new_path)

    def map_by_size(self, source):
        yield "Mapping by size"
        f_map = {size: [] for size in reversed(self.sized_dirs)}
        for root, sub_folders, files in os.walk(source):
            for file in files:
                found = False
                f_path = os.path.join(root, file)
                x = get_image_size(f_path)
                for size in f_map:
                    if not found:
                        if x >= size:
                            f_map[size].append(f_path)
                            found = True
        self.f_map = f_map
        return f_map

    def map_by_res(self, source):
        yield "Mapping by res"
        f_map = {size: [] for size in reversed(self.sized_dirs)}
        for root, sub_folders, files in os.walk(source):
            for file in files:
                found = False
                f_path = os.path.join(root, file)
                x, y = get_image_resolution(f_path)
                for size in f_map:
                    if not found:
                        if x >= size or y >= size:
                            f_map[size].append(f_path)
                            found = True
        self.f_map = f_map
        return f_map
