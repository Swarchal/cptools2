"""
Class for extracting simple plate metadata from the image filenames.

author: Scott Warchal
date: 2020-01-27
"""

import os
import string
from collections import namedtuple


class MetadataParser(object):
    """
    Extract metadata from microscope filepaths.
    This class when initiated with a microscope argument has two methods
    to parse a single filepath `parse_filepath()`, or parse a list of filepaths
    `parse_filepath_list()`
    """
    def __init__(self, microscope):
        microscope = microscope.strip().lower()
        microscope_mapper = {
            "ix": "imagexpress",
            "imagexpress": "imagexpress",
            "imageexpress": "imagexpress",
            "moldev": "imagexpress",
            "moleculardevices": "imagexpress",
            "yoko": "yokogawa",
            "yokogawa": "yokogawa",
            "cv8000": "yokogawa",
            "cv7000": "yokogawa",
            "opera": "opera",
            "columbus": "opera",
            "harmony": "opera"
        }
        parser_mapper = {
            "imagexpress": self.parse_ix,
            "yokogawa": self.parse_yokogawa,
            "opera": self.parse_opera
        }
        valid_microscopes = list(microscope_mapper.keys())
        if microscope not in valid_microscopes:
            err_msg = "unknown microscope, options = {}"
            raise ValueError(err_msg.format(valid_microscopes))
        # standardise microscope name
        self.microscope = microscope_mapper[microscope]
        self.parse_func = parser_mapper[self.microscope]
        self.metadata_names = [
            "Metadata_well",
            "Metadata_row",
            "Metadata_column",
            "Metadata_site",
            "Metadata_plate",
            "Metadata_z",
            "Metadata_channel",
            "path",
            "URL"
        ]

    @staticmethod
    def get_row(well_str):
        return ord(well_str.lower()[0]) - 96

    @staticmethod
    def get_column(well_str):
        return int(well_str[1:])

    @staticmethod
    def row_column_to_well(row, column):
        letters = string.ascii_uppercase
        return "{}{:02d}".format(letters[row-1], column)

    def parse_channel(self, x):
        """needed for the splitter functions which group by channel number"""
        final_path = os.path.basename(x)
        if self.microscope == "imagexpress":
            return int(final_path.split("_")[3][1])
        elif self.microscope == "yokogawa":
            plate, well, rest = final_path.split("_")
            return int(rest[-2:])
        elif self.microscope == "opera":
            channel = int(final_path.replace(".tif", "")[16:])
        else:
            raise RuntimeError()

    def parse_ix(self, x):
        final_path = os.path.basename(x)
        path = os.path.dirname(x)
        output = namedtuple("ImageXpress", self.metadata_names)
        well = final_path.split("_")[1]
        row = self.get_row(well)
        column = self.get_column(well)
        site = int("".join(i for i in final_path.split("_")[2] if i.isdigit()))
        plate = x.split(os.sep)[-4]
        z = 1 # non-confocal ImageXpress
        channel = int(x.split("_")[3][1])
        return output(well, row, column, site, plate, z, channel, path, final_path)

    def parse_yokogawa(self, x):
        output = namedtuple("Yokogawa", self.metadata_names)
        final_path = os.path.basename(x)
        path = os.path.dirname(x)
        plate, well, rest = final_path.split("_")
        row = self.get_row(well)
        column = self.get_column(well)
        site = int(rest[6:9])
        z = int(rest[16:18])
        channel = int(rest[-2:])
        return output(well, row, column, site, plate, z, channel, path, final_path)

    def parse_opera(self, x):
        output = namedtuple("Opera", self.metadata_names)
        final_path = os.path.basename(x)
        path = os.path.dirname(x)
        row = int(final_path[1:3])
        column = int(final_path[4:6])
        well = self.row_column_to_well(row, column)
        site = int(final_path.split("-")[1])
        plate = x.split(os.sep)[-2]
        z = int(final_path[13:15])
        channel = int(final_path.replace(".tif", "")[16:])
        return output(well, row, column, site, plate, z, channel, path, final_path)

    def parse_filepath(self, filepath):
        """generic extract metadata from filepath"""
        return self.parse_func(filepath)

    def parse_filepath_list(self, filepath_list):
        """generatic extract metadata from a list of filepaths"""
        return [self.parse_func(i) for i in filepath_list]

