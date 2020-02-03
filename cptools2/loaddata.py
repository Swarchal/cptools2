"""
Create dataframes/csv-files for CellProfiler's LoadData module
"""

import pandas as _pd
from cptools2 import utils
from cptools2 import parse_metadata


def create_loaddata(img_list, microscope, channel_dict=None):
    """
    create a dataframe suitable for cellprofilers LoadData module

    Parameters:
    -----------
    img_list: list
    microscope: str

    Returns:
    --------
    pandas DataFrame
    """
    df_long = create_long_loaddata(img_list, microscope)
    return cast_dataframe(df_long, channel_dict)


def create_long_loaddata(img_list, microscope):
    """
    create a dataframe of image paths with metadata columns

    Parameters:
    -----------
    img_list: list
        list of image paths
    microscope: str
        which microscope, needed to parse metadata from filepaths

    Returns:
    --------
    pandas DataFrame
    """
    parser = parse_metadata.MetadataParser(microscope)
    df_img = _pd.DataFrame(parser.parse_filepath_list(img_list))
    return df_img


def cast_dataframe(dataframe, channel_dict=None, check_nan=True):
    """
    reshape a create_loaddata dataframe from long to wide format

    Parameters:
    -----------
    dataframe: pandas DataFrame
    check_nan: Boolean (default = True)
        whether to raise a warning if the dataframe contains
        any missing values
    channel_dict: Dict
        a mapping of channel numbers to channel names from the config
        file. This is optional and if not present the channels will be
        labelled after the channel numbers extracted from the metadata.

    Returns:
    --------
    pandas DataFrame
    """
    channels = sorted(list(set(dataframe.Metadata_channel)))
    wide_df = dataframe.pivot_table(
        index=[
            "Metadata_well",
            "Metadata_row",
            "Metadata_column",
            "Metadata_site",
            "Metadata_plate",
            "Metadata_z",
            "path"
        ],
        columns="Metadata_channel",
        values="URL",
        aggfunc="first").reset_index()
    # rename FileName columns from 1, 2... to FileName_W1, FileName_W2 ...
    columns = {}
    for i in channels:
        if channel_dict is None:
            columns[i] = "FileName_W{0}".format(str(i))
        else:
            columns[i] = "FileName_{}".format(channel_dict[i])
    wide_df.rename(columns=columns, inplace=True)
    # duplicate PathName for each channel
    for i in channels:
        if channel_dict is None:
            wide_df["PathName_W" + str(i)] = wide_df.path
        else:
            wide_df["PathName_{}".format(channel_dict[i])] = wide_df.path
    wide_df.drop(["path"], axis=1, inplace=True)
    if check_nan is True:
        if utils.any_nan_values(dataframe):
            raise LoadDataError("dataframe contains missing values")
    expected_rows = dataframe.shape[0] // len(channels)
    check_dataframe_size(wide_df, expected_rows)
    return wide_df


def check_dataframe_size(dataframe, expected_rows):
    """
    docstring

    Parameters:
    -----------
    dataframe
    expected_rows

    Returns:
    --------
    nothing, raises RuntimeError
    """
    n_rows_in_dataframe = dataframe.shape[0]
    if n_rows_in_dataframe != expected_rows:
        msg = "LoadData dataframe has an unexpected number of rows, expected: {}, got: {}"
        if n_rows_in_dataframe > expected_rows:
            msg += "\nDo your images have the same number of z-planes per channel?"
        raise LoadDataError(msg.format(expected_rows, n_rows_in_dataframe))


class LoadDataError(Exception):
    pass
