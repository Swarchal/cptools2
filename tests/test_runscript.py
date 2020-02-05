import os
import subprocess

CURRENT_PATH = os.path.dirname(__file__)

def test_run_cptools2():
    config_path = os.path.join(CURRENT_PATH, "test_config2.yaml")
    return_val = subprocess.call(
        ["env", "SGE_CLUSTER_NAME=idrs", "cptools2", config_path]
    )
    assert return_val == 0

def test_run_cptools2_duplicate_plate():
    config_path = os.path.join(CURRENT_PATH, "test_config_duplicate.yaml")
    return_val = subprocess.call(
        ["env", "SGE_CLUSTER_NAME=idrs", "cptools2", config_path]
    )
    assert return_val == 0


def test_run_cptools2_duplicate_plate_removed():
    config_path = os.path.join(CURRENT_PATH, "test_config_duplicate_removed.yaml")
    return_val = subprocess.call(
        ["env", "SGE_CLUSTER_NAME=idrs", "cptools2", config_path]
    )
    assert return_val == 0
