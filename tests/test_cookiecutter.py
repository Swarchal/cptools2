"""
module docstring
"""

from cptools2 import cookiecutter
import os

N_TASKS = 3
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
COMMANDS_LOC = os.path.join(THIS_DIR, "cookiecutter_commands.txt")


def test_SGEScript():
    """test setting attributes"""
    my_script = cookiecutter.SGEScript(
        name="test_script", user="test_user", runtime="06:00:00"
    )
    assert my_script.name == "test_script"
    assert my_script.runtime == "06:00:00"
    assert my_script.queue == "lungo.q"
    assert my_script.user == "test_user"
    assert isinstance(my_script.template, str)
    my_script += "#$ -another_option"
    # add __iadd__ adds a final "\n" to the added text, when splitting by "\n"
    # we need to look for the second to last element, as the last one if just
    # and empty string
    assert my_script.template.split("\n")[-2] == "#$ -another_option"
    # test that the __iadd__ method works as expected
    my_script += "python example.py"
    assert my_script.template.split("\n")[-2] == "python example.py"


def test_SGEScript_mock_cluster():
    """Test auto-detecting user if we're on the cluster."""
    os.environ["SGE_CLUSTER_NAME"] = "idrs"
    my_script = cookiecutter.SGEScript(name="mock_cluster")
    assert my_script.user == os.environ["USER"]
    user = os.environ["USER"]
    expected_output_location = "/scratch/{}/".format(user)
    assert my_script.output == expected_output_location


def test_SGEScript_loop_through_file():
    """test creating array job script"""
    script_tasks = cookiecutter.SGEScript(user="user", tasks="1-100")
    script_tasks.loop_through_file(input_file="commands.txt")
    output = script_tasks.template.split("\n")
    assert output[-4] == 'CP_COMMAND_LIST="commands.txt"'
    assert output[-3] == 'CP_COMMAND=$(awk "NR==$SGE_TASK_ID" "$CP_COMMAND_LIST")'
    assert output[-2] == "$CP_COMMAND"
    assert "#$ -t 1-100" in output
    assert script_tasks.array is True


def test_SGEScript_set_tasks():
    """check different methods of adding tasks work"""
    task_int = cookiecutter.SGEScript(user="user", tasks=42)
    assert "#$ -t 1-42" in task_int.template
    task_list = cookiecutter.SGEScript(user="user", tasks=[12, 32])
    assert "#$ -t 12-32" in task_list.template
    # check that tasks are inferred is tasks are missing set
    # if the input_file is readable
    task_infer = cookiecutter.SGEScript(user="user")
    task_infer.loop_through_file(COMMANDS_LOC)
    assert task_infer.array is True
    assert task_infer.tasks == "#$ -t 1-{}".format(N_TASKS)

