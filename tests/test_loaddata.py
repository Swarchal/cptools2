import os
import pandas as pd
from cptools2 import loaddata
from cptools2 import filelist

CURRENT_PATH = os.path.dirname(__file__)
TEST_PATH = os.path.join(CURRENT_PATH, "example_dir")
TEST_PATH_PLATE_1 = os.path.join(TEST_PATH, "test-plate-1")
IMG_LIST = filelist.files_from_plate(TEST_PATH_PLATE_1)


def test_create_long_loaddata():
    """cptool2.loaddata.create_long_loaddata(img_list)"""
    long_df = loaddata.create_long_loaddata(IMG_LIST, microscope="imagexpress")
    assert isinstance(long_df, pd.DataFrame)
    assert long_df.shape[0] == len(IMG_LIST)


def test_cast_dataframe():
    """cptools2.loaddata.cast_dataframe(dataframe)"""
    long_df = loaddata.create_long_loaddata(IMG_LIST, microscope="imagexpress")
    wide_df = loaddata.cast_dataframe(long_df)
    assert isinstance(wide_df, pd.DataFrame)
    # check we have a row per imageset
    expected_rows = 60 * 6
    wide_df.to_csv("/home/swl_sur/test.csv")
    assert wide_df.shape[0] == expected_rows
    expected_cols = sorted(["Metadata_site",
                            "Metadata_row",
                            "Metadata_column",
                            "Metadata_z",
                            "Metadata_well",
                            "Metadata_plate",
                            "FileName_W1",
                            "FileName_W2",
                            "FileName_W3",
                            "FileName_W4",
                            "FileName_W5",
                            "PathName_W1",
                            "PathName_W2",
                            "PathName_W3",
                            "PathName_W4",
                            "PathName_W5"])
    assert sorted(wide_df.columns.tolist()) == expected_cols


def test_create_loaddata():
    """cptools2.loaddata.create_loaddata(img_list)"""
    output = loaddata.create_loaddata(IMG_LIST, microscope="imagexpress")
    # make our own
    long_df = loaddata.create_long_loaddata(IMG_LIST, microscope="imagexpress")
    wide_df = loaddata.cast_dataframe(long_df)
    assert output.equals(wide_df)

