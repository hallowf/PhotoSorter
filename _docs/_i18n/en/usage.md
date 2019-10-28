# Usage

PhotoSorter is based of [sort-PhotorecRecoveredFiles](https://github.com/tfrdidi/sort-PhotorecRecoveredFiles)

You will need to provide it with the directory of all the pictures to sort and a directory to copy the files over and sort them,
PhotoSorter does not remove your old files so make sure you have the required disk space.

Then the sorter starts searching trough those directories and subsequent folders,
copies them over to the destination and if a date is found that does not equal "today" as of the day you are running PhotoSorter
a new folder with the year is created and the file is copied to that folder if a date isn't found
the file is moved to a folder called unknown.

Finally if you choose to sort the remaining "unknown" files, you can select either size or resolution,
those files will be copied to new folders with the respective size in MB or resolution