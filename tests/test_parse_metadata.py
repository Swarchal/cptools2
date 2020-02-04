from cptools2 import parse_metadata
import pytest


def test_parse_channel():
    pass


def test_parse_ix():
    pass


def test_parse_yoko():
    pass


def test_parse_opera():
    pass


def test_guess_microscope_ix():
    test_path = "/path/to/experiment name_B02_s1_w1AD0ABEBC-3BA8-4199-9431-041A4D5B8C32.tif"
    output = parse_metadata.guess_microscope(test_path)
    assert output == "imagexpress"


def test_guess_microscope_yoko():
    test_path = "some/path/A000002-PC_C03_T0001F001L01A01Z01C01.tif"
    output = parse_metadata.guess_microscope(test_path)
    assert output == "yokogawa"


def test_guess_microscope_opera():
    test_path = "/some/path/001002-1-001001001.tif"
    output = parse_metadata.guess_microscope(test_path)
    assert output == "opera"


def test_guess_microscope_nonesense():
    test_path = "thisis_not_a_valid_path01.tif"
    with pytest.raises(RuntimeError):
        parse_metadata.guess_microscope(test_path)

