"""
module docstring
"""

import os
from collections import namedtuple


class MetadataParser(object):
    """
    Extract metadata from microscope filepaths.
    This class when initiated with a microscope argument has two methods
    to parse a single filepath `parse_filepath()`, or parse a list of filepaths
    `parse_filepath_list()`
    """
    def __init__(self, microscope):
        valid_microscopes = [
            "ix",
            "imagexpress",
            "imageexpress",
            "yoko",
            "yokogawa",
            "cv8000",
            "cv7000",
            "opera",
            "columbus",
            "harmony"
        ]
        microscope_mapper = {
            "ix": "imagexpress",
            "imagexpress": "imagexpress",
            "imageexpress": "imagexpress",
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
        if microscope.lower() not in valid_microscopes:
            err_msg = "unknown microscope, valid options = {}"
            raise ValueError(err_msg.format(valid_microscopes))
        self.microscope = microscope_mapper[microscope.lower()]
        self.parse_func = parser_mapper[self.microscope]

    @staticmethod
    def parse_ix(x):
        output = namedtuple(
            "ImageXpress",
            ["well", "row", "column", "site", "plate", "z", "channel", "path"]
        )
        well = os.path.basename(x).split("_")[1]
        row = self.get_row(well)
        column = self.get_column(well)
        site = int("".join(i for i in os.path.basename(x).split("_")[2] if i.isdigit()))
        plate = x.split(os.sep)[-4]
        z = 1 # non-confocal ImageXpress
        channel = int(x.split("_")[3][1])
        return output(well, row, column, site, plate, z, channel, x)

    @staticmethod
    def parse_yokogawa(x):
        output = namedtuple(
            "Yokogawa",
            ["well", "row", "column", "site", "plate", "z", "channel", "path"]
        )
        final_path = os.path.basename(x)
        plate, well, rest = final_path.split("_")
        row = self.get_row(well)
        column = self.get_column(well)
        site = int(rest[6:9])
        z = int(rest[16:18])
        channel = int(rest[-2:])
        return output(well, row, column, site, plate, z, channel, x)

    @staticmethod
    def parse_opera(x):
        output = namedtuple(
            "Opera",
            ["well", "row", "column", "site", "plate", "z", "channel", "path"]
        )
        final_path = os.path.basename(x)
        row = int(final_path[1:3])
        column = int(final_path[4:6])
        well = self.row_column_to_well(row, column)
        site = int(final_path.split("-")[1])
        plate = x.split(os.sep)[-2]
        z = int(finalpath[13:15])
        channel = int(final_path.replace(".tif", "")[16:])
        return output(well, row, column, site, plate, z, channel, x)

    @staticmethod
    def get_row(well_str):
        return ord(well_str.lower())[0] - 96

    @staticmethod
    def get_column(well_str):
        return int(well_str[1:])

    @staticmethod
    def row_column_to_well(row, column):
        letters = string.ascii_uppercase
        return "{}{:02d}".format(letters[row-1], column)

    def parse_filepath(self, filepath):
        """generic extract metadata from filepath"""
        return self.parse_func(filepath)

    def parse_filepath_list(self, filepath_list):
        """generatic extract metadata from a list of filepaths"""
        return [self.parse_func(i) for i in filepath_list]

