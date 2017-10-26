"""
Generate eddie submission scripts for the
staging, analysis and destaging jobs
"""

import os
import textwrap
from datetime import datetime
from scissorhands import script_generator
from cptools2 import utils


def make_command_paths(commands_location):
    """
    create the paths to the commands
    """
    names = ["staging", "cp_commands", "destaging"]
    return {name: os.path.join(commands_location, name+".txt") for name in names}


def _lines_in_commands(staging, cp_commands, destaging):
    """
    Number of lines in each of the commands file.
    While the number of lines in each of the files *should* be the same,
    it's worth checking.

    Parameters:
    -----------
    staging: string
        path to staging commands

    cp_commands: string
        path to cellprofiler commands

    destaging: string
        path to destaging commands

    Returns:
    --------
    Dictionary, e.g:
        {staging: 128, cp_commands: 128, destaging: 128}
    """
    names = ["staging", "cp_commands", "destaging"]
    paths = [staging, cp_commands, destaging]
    counts = [utils.count_lines_in_file(i) for i in paths]
    # check if the counts differ
    if len(set(counts)) > 1:
        raise RuntimeWarning("command files contain differing number of lines")
    return {name: count for name, count in zip(names, counts)}


def lines_in_commands(commands_location):
    """
    Given a path to a directory which contains the commands:
        1. staging
        2. cellprofiler commands
        3. destaging
    This will return the number of lines in each of these text files.

    Parameters:
    -----------
    commands_location: string
        path to directory containing commands

    Returns:
    ---------
    Dictionary

        {"staging":     int,
         "cp_commands": int,
         "destaging":   int}
    """
    command_paths = make_command_paths(commands_location)
    print("** saving commands at '{}'".format(commands_location))
    return _lines_in_commands(**command_paths)


def load_module_text():
    """returns load module commands"""
    user = os.environ["USER"]
    try:
        venv_path = venv_store[user]
        print("** known user, inserting {}'s CellProfiler virtual environment path in analysis script".format(user))
    except KeyError:
        venv_path = "# unknown user, insert path to Cellprofiler virtual environment here"
        print("** unknown user")
        print("\t ** unable to insert path to Cellprofiler virtual environment in the analysis script")
    return textwrap.dedent(
        """
        module load igmm/apps/hdf5/1.8.16
        module load igmm/apps/python/2.7.10
        module load igmm/apps/jdk/1.8.0_66
        module load igmm/libs/libpng/1.6.18

        # activate the cellprofiler virtualenvironment
        # NOTE: might have to modify this for individual users to point to your
        #       envirtual environment
        source {venv_path}
        """.format(venv_path=venv_path)
    )


def make_qsub_scripts(commands_location, commands_count_dict):
    """
    Create and save qsub submission scripts in the same location as the
    commands.

    Parameters:
    -----------
    commands_location: string
        path to directory that contains staging, cp_commands, and destaging
        command files.

    commands_count_dict: dictionary
        dictionary of the number of commands contain in each of the jobs


    Returns:
    ---------
    Nothing, writes files to `commands_location`
    """
    cmd_path = make_command_paths(commands_location)
    time_now = datetime.now().replace(microsecond=0)
    time_now = str(time_now).replace(" ", "-")
    # append random hex to job names - this allows you to run multiple jobs
    # without the -hold_jid flags fron clashing
    job_hex = script_generator.generate_random_hex()
    # FIXME: using AnalysisScript class for everything, due to the 
    #        {Staging, Destaging}Script class not having loop_through_file
    stage_script = script_generator.AnalysisScript(
        name="staging_{}".format(job_hex),
        memory="1G",
        tasks=commands_count_dict["staging"]
    )
    stage_script.template += "#$ -q staging\n"
    stage_script.loop_through_file(cmd_path["staging"])
    stage_loc = os.path.join(commands_location,
                             "{}_staging_script.sh".format(time_now))
    print("** saving staging submission script at '{}'".format(stage_loc))
    stage_script.save(stage_loc)

    analysis_script = script_generator.AnalysisScript(
        name="analysis_{}".format(job_hex),
        tasks=commands_count_dict["cp_commands"],
        hold_jid_ad="staging_{}".format(job_hex),
        pe="sharedmem 1",
        memory="12G"
    )
    analysis_script.template += load_module_text()
    analysis_script.loop_through_file(cmd_path["cp_commands"])
    analysis_loc = os.path.join(commands_location,
                                "{}_analysis_script.sh".format(time_now))
    print("** saving analysis submission script at '{}'".format(analysis_loc))
    analysis_script.save(analysis_loc)

    destaging_script = script_generator.AnalysisScript(
        name="destaging_{}".format(job_hex),
        memory="1G",
        hold_jid="analysis_{}".format(job_hex),
        tasks=commands_count_dict["destaging"]
    )
    destaging_script.loop_through_file(cmd_path["destaging"])
    destage_loc = os.path.join(commands_location,
                               "{}_destaging_script.sh".format(time_now))
    print("** saving destaging submission script at '{}'".format(destage_loc))
    destaging_script.save(destage_loc)


venv_store = {
    "s1027820": "/exports/igmm/eddie/Drug-Discovery/virtualenv-1.10/myVE/bin/activate",
    # TODO: check this, might not be correct
    "s1117349": "/exports/igmm/eddie/Drug-Discovery/Becka/virtualenv-1.10/myVE/bin/activate"
}

