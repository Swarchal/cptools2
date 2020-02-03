import os
import pytest
from cptools2 import parse_config


CURRENT_PATH = os.path.dirname(__file__)
TEST_PATH = os.path.join(CURRENT_PATH, "test_config.yaml")
TEST_BROKEN = os.path.join(CURRENT_PATH, "test_config_broken.yaml")


def test_open_yaml():
    config = parse_config.Config(TEST_PATH)
    config_dict = config.config_dict
    assert isinstance(config_dict, dict)


def test_check_yaml_args():
    with pytest.raises(ValueError):
        config = parse_config.Config(TEST_BROKEN)


def test_experiment():
    config = parse_config.Config(TEST_PATH)
    assert config.experiment == "/path/to/experiment"


def test_chunk():
    config = parse_config.Config(TEST_PATH)
    assert config.chunk == 46


def test_add_plate():
    config = parse_config.Config(TEST_PATH)
    assert config.add_plate == {"exp_dir" : "/path/to/new/experiment",
                                "plates" : ["plate_3", "plate_4"]}


def test_remove_plate():
    config = parse_config.Config(TEST_PATH)
    assert config.remove_plate == ["plate_1", "plate_2"]


def test_create_commands():
    config = parse_config.Config(TEST_PATH)
    pipeline_loc = os.path.abspath("./tests/example_pipeline.cppipe")
    expected = {
        "pipeline" : pipeline_loc,
        "location" : "/example/location",
        "commands_location" : "/home/user",
        "job_size": 46,
        "channel_dict": None,
    }
    assert config.create_command_args() == expected

