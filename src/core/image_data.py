import os
from PIL import Image


def get_minimum_creation_time(exif_data):
    creation_time = None
    date_time = exif_data.get('DateTime')
    date_time_original = exif_data.get('EXIF DateTimeOriginal')
    date_time_digitized = exif_data.get('EXIF DateTimeDigitized')

    # 3 different time fields that can be set independently result in 9 if-cases
    if (date_time is None):
        if (date_time_original is None):
            # case 1/9: dateTime, dateTimeOriginal,
            # and dateTimeDigitized = None
            # case 2/9: dateTime and dateTimeOriginal = None,
            # then use dateTimeDigitized
            creation_time = date_time_digitized
        else:
            # case 3/9: dateTime and dateTimeDigitized = None,
            # then use dateTimeOriginal
            # case 4/9: dateTime = None, prefere dateTimeOriginal
            # over dateTimeDigitized
            creation_time = date_time_original
    else:
        # case 5-9: when creationTime is set, prefere it over the others
        creation_time = date_time

    return creation_time


def get_image_resolution(image):
    res = None
    try:
        with Image.open(image) as img:
            width, height = img.size
            res = (width, height)
    except Exception as e:
        raise e
    return res


def get_image_size(image):
    size = None
    try:
        size = os.stat(image).st_size
    except Exception as e:
        raise e
    return size
