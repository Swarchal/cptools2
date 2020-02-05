import os
from cptools2 import filelist

CURRENT_PATH = os.path.dirname(__file__)
TEST_PATH_IX = os.path.join(CURRENT_PATH, "example_dir_ix")
filelister_ix = filelist.Filelist("imagexpress")

def test_files_from_plate():
    """see if we get image files from a plate directory"""
    plate_path = os.path.join(TEST_PATH_IX, "test-plate-1")
    output = filelister_ix.files_from_plate(plate_path)
    assert len(output) > 0
    for f in output:
        assert f.endswith(".tif")


def test_files_from_plate_truncate():
    """files_from_plate with truncated file-paths"""
    plate_path = os.path.join(TEST_PATH_IX, "test-plate-1")
    output = filelister_ix.files_from_plate(plate_path)
    for f in output:
        assert len(f.split(os.sep)) == 4


def test_paths_to_plates():
    """
    check paths_to_plates
    though don't actually know what the absolute path is going to be
    on other computers...
    """
    output = filelister_ix.paths_to_plates(TEST_PATH_IX)
    prefix = os.path.abspath(TEST_PATH_IX)
    plate_names = ["test-plate-1", "test-plate-2",
                   "test-plate-3", "test-plate-4"]
    make_own = [os.path.join(prefix, name) for name in plate_names]
    assert len(output) == len(plate_names)
    for ans in output:
        assert ans in make_own

# yoko
TEST_PATH_YOKO = os.path.join(CURRENT_PATH, "example_dir_yoko/")
filelister_yoko = filelist.Filelist("yokogawa")

def test_files_from_plate_yoko():
    """see if we get image files from a plate directory"""
    plate_path = os.path.join(
       TEST_PATH_YOKO,
        "screen-name-batch1_20190213_095340/A000002-PC"
    )
    output = filelister_yoko.files_from_plate(plate_path)
    assert len(output) > 0
    for f in output:
        assert f.endswith(".tif")


def test_paths_to_plates():
    """
    check paths_to_plates
    though don't actually know what the absolute path is going to be
    on other computers...
    """
    output = filelister_yoko.paths_to_plates(TEST_PATH_YOKO)
    prefix = os.path.abspath(TEST_PATH_YOKO)
    plate_names = ["screen-name-batch1_20190213_095340/A000002-PC"]
    make_own = [os.path.join(prefix, name) for name in plate_names]
    assert len(output) == len(plate_names)
    for ans in output:
        assert ans in make_own
