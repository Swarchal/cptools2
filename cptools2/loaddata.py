"""
Create dataframes/csv-files for CellProfiler's LoadData module
"""

import textwrap

import pandas as _pd
from cptools2 import utils
from cptools2 import parse_metadata


def create_loaddata(img_list, microscope):
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
    return cast_dataframe(df_long)


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


def cast_dataframe(dataframe, check_nan=True):
    """
    reshape a create_loaddata dataframe from long to wide format

    Parameters:
    -----------
    dataframe: pandas DataFrame
    check_nan: Boolean (default = True)
        whether to raise a warning if the dataframe contains
        any missing values

    Returns:
    --------
    pandas DataFrame
    """
    n_channels = len(set(dataframe.Metadata_channel))
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
    for i in range(1, n_channels+1):
        columns[i] = "FileName_W{0}".format(str(i))
    wide_df.rename(columns=columns, inplace=True)
    # duplicate PathName for each channel
    for i in range(1, n_channels+1):
        wide_df["PathName_W" + str(i)] = wide_df.path
    wide_df.drop(["path"], axis=1, inplace=True)
    if check_nan is True:
        if utils.any_nan_values(dataframe):
            raise LoadDataError("dataframe contains missing values")
    return wide_df


def check_dataframe_size(dataframe, min_rows=None):
    """
    check that a dataframe contains at least `min_rows` of data, raise
    an error if this is not the case.

    Parameters:
    ------------
    dataframe: pandas.DataFrame
        dataframe to check
    min_rows: int (default = None)
        minimum number of rows the dataframe should contain. If None then
        an Error will never be raised.

    Returns:
    --------
    Raises a `LoadDataError` or nothing
    """
    nrow = dataframe.shape[0]
    if nrow < min_rows:
        msg = """Too few rows detected in a LoadData dataframe. Expected at
                 least {} rows, actual: {}""".format(min_rows, nrow)
        raise LoadDataError(textwrap.dedent(msg))


class LoadDataError(Exception):
    pass
