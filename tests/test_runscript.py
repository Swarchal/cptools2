import os
import subprocess

CURRENT_PATH = os.path.dirname(__file__)
TEST_CONFIG_PATH = os.path.join(CURRENT_PATH, "test_config2.yaml")

def test_run_cptools2():
    return_val = subprocess.call(
        ["env", "SGE_CLUSTER_NAME=idrs", "cptools2", TEST_CONFIG_PATH]
    )
    assert return_val == 0

