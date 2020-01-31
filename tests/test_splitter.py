import os
from cptools2 import splitter
from cptools2 import filelist


# need to have an image list
CURRENT_PATH = os.path.dirname(__file__)
TEST_PATH = os.path.join(CURRENT_PATH, "example_dir_ix")
TEST_PATH_PLATE_1 = os.path.join(TEST_PATH, "test-plate-1")
# just use a single plate
filelister = filelist.Filelist("imagexpress")
IMG_LIST = filelister.files_from_plate(TEST_PATH_PLATE_1)
IMG_LIST = [i for i in IMG_LIST if i.endswith(".tif")]


def test_group_images():
    """job_splitter._group_images(df_img)"""
    # create dataframe for _group_images
    df_img = splitter._well_site_table(IMG_LIST)
    output = splitter._group_images(df_img)
    assert isinstance(output, list)
    # list should be the number of sites per well by the number of wells
    n_well_sites = 60 * 6
    assert len(output) == n_well_sites
    # check we have 5 channels
    assert len(output[0]) == 5
    # check channels are grouped in the same well/site
    for i in output[0]:
        assert i.startswith("test-plate-1/2015-07-31/4016/val screen_B02_s1")
    for i in output[1]:
        assert i.startswith("test-plate-1/2015-07-31/4016/val screen_B02_s2")


def test_chunks():
    """cptools2.splitter.chunks() on simulated data"""
    # test is works on a stupid dataset
    test_data = list(range(100))
    chunked_test_data = splitter.chunks(test_data, job_size=10)
    output = [i for i in chunked_test_data]
    assert len(output) == 10
    for i in output:
        assert len(i) == 10
    # on data with some with some left-over in final bin
    test_data_2 = list(range(109))
    chunk_test_data_2 = splitter.chunks(test_data_2, job_size=10)
    output2 = [i for i in chunk_test_data_2]
    assert len(output2) == 11
    for i in output2[:-1]:
        assert len(i) == 10
    assert len(output2[-1]) == 9


def test_split():
    """cptools2.splitter.split()"""
    job_size = 96
    output = splitter.split(IMG_LIST, job_size)
    assert len(output[0]) == job_size
    for job in output[:-1]:
        assert len(job) == job_size
