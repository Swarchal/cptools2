import os
import pandas as pd
from cptools2 import loaddata
from cptools2 import filelist

CURRENT_PATH = os.path.dirname(__file__)

################################################################################
# imagexpress
################################################################################

TEST_PATH_IX = os.path.join(CURRENT_PATH, "example_dir_ix")
TEST_PATH_PLATE_1_IX = os.path.join(TEST_PATH_IX, "test-plate-1")
filelister_ix = filelist.Filelist("imagexpress")
IMG_LIST_IX = filelister_ix.files_from_plate(TEST_PATH_PLATE_1_IX)


def test_create_long_loaddata_ix():
    """cptool2.loaddata.create_long_loaddata(img_list)"""
    long_df = loaddata.create_long_loaddata(IMG_LIST_IX, microscope="imagexpress")
    assert isinstance(long_df, pd.DataFrame)
    assert long_df.shape[0] == len(IMG_LIST_IX)


def test_cast_dataframe_ix():
    """cptools2.loaddata.cast_dataframe(dataframe)"""
    long_df = loaddata.create_long_loaddata(IMG_LIST_IX, microscope="imagexpress")
    wide_df = loaddata.cast_dataframe(long_df)
    assert isinstance(wide_df, pd.DataFrame)
    # check we have a row per imageset
    expected_rows = 60 * 6
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


def test_create_loaddata_ix():
    """cptools2.loaddata.create_loaddata(img_list)"""
    output = loaddata.create_loaddata(IMG_LIST_IX, microscope="imagexpress")
    # make our own
    long_df = loaddata.create_long_loaddata(IMG_LIST_IX, microscope="imagexpress")
    wide_df = loaddata.cast_dataframe(long_df)
    assert output.equals(wide_df)


################################################################################
# yoko
################################################################################

TEST_PATH_YOKO = os.path.join(CURRENT_PATH, "example_dir_yoko")
TEST_PATH_PLATE_1_YOKO = os.path.join(
    TEST_PATH_YOKO,
    "screen-name-batch1_20190213_095340/A000002-PC/"
)
filelister_yoko = filelist.Filelist("yokogawa")
IMG_LIST_YOKO = filelister_yoko.files_from_plate(TEST_PATH_PLATE_1_YOKO)


def test_create_long_loaddata_yoko():
    """cptool2.loaddata.create_long_loaddata(img_list)"""
    long_df = loaddata.create_long_loaddata(IMG_LIST_YOKO, microscope="yokogawa")
    assert isinstance(long_df, pd.DataFrame)
    assert long_df.shape[0] == len(IMG_LIST_YOKO)


def test_cast_dataframe_yoko():
    """cptools2.loaddata.cast_dataframe(dataframe)"""
    long_df = loaddata.create_long_loaddata(IMG_LIST_YOKO, microscope="yokogawa")
    wide_df = loaddata.cast_dataframe(long_df)
    assert isinstance(wide_df, pd.DataFrame)
    # check we have a row per imageset
    # FIXME: check how many rows we expect for the yokogawa plate
    expected_rows = 60 * 6
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
                            "PathName_W1",
                            "PathName_W2",
                            "PathName_W3",
                            "PathName_W4"])
    assert sorted(wide_df.columns.tolist()) == expected_cols


def test_case_dataframe_yoko():
    """cptools2.loaddata.create_loaddata(img_list)"""
    output = loaddata.create_loaddata(IMG_LIST_YOKO, microscope="yokogawa")
    # make our own
    long_df = loaddata.create_long_loaddata(IMG_LIST_YOKO, microscope="yokogawa")
    wide_df = loaddata.cast_dataframe(long_df)
    assert output.equals(wide_df)


################################################################################
# opera
################################################################################

#TEST_PATH_OPERA = os.path.join(CURRENT_PATH, "example_dir_opera")
#TEST_PATH_PLATE_1_OPERA = os.path.join(TEST_PATH_OPERA, "test-plate-1")
# filelister_opera = filelist.Filelist("opera")
#IMG_LIST_OPERA = filelister_opera.files_from_plate(TEST_PATH_PLATE_1_OPERA)


def test_create_long_loaddata_opera():
    assert False


def test_cast_dataframe_opera():
    assert False


def test_case_dataframe_opera():
    assert False

