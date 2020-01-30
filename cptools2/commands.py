import os

from cptools2 import utils


def make_cp_cmnd(name, pipeline, location, output_loc):
    """
    create cellprofiler command

    Parameters:
    -----------
    name: string
        name of the individual job
    pipeline: string
        filepath to the cellprofiler pipeline
    location: string
        filepath to the directory which contains the loaddata csv files
    output_loc: string
        where to store the results from the cellprofiler job

    Returns:
    --------
    string: a cellprofiler command
    """
    loaddata_name = os.path.join(location, "loaddata", name)
    cmnd = cp_command(pipeline=pipeline,
                      load_data=loaddata_name + ".csv",
                      output_location=output_loc)
    return cmnd


def write_loaddata(name, location, dataframe, fix_paths=True):
    """
    write a loaddata csv file to disk

    Parameters:
    -----------
    name: string
        name of the individual job
    location: string
        filepath to the directory which contains the loaddata csv files
    dataframe: pandas.DataFrame
        a dataframe suitable for Cellprofiler's LoadData module
    fix_paths: Boolean (default = True)
        whether to prefix the filepaths in a loaddata dataframe so that
        the paths point to the image location after the images have been staged

    Returns:
    --------
    nothing, writes the csv file to disk
    """
    loaddata_name = os.path.join(location, "loaddata", name + ".csv")
    if fix_paths is True:
        dataframe = utils.prefix_filepaths(dataframe, name, location)
    dataframe.to_csv(loaddata_name, index=False)


def _write_single(commands_location, commands, final_name):
    """
    write commands for single command list

    Parameters:
    -----------
    commands_location: string
        directory where to save the commands
    commands:
        list of commands to write to disk
    final_name:
        filename, what to call the commands file. This is joined to
        commands_location, e.g: `commands_location`/`file_name`.txt

    Returns:
    --------
    nothing, writes commands to disk
    """
    cmnd_loc = os.path.join(commands_location, final_name + ".txt")
    with open(cmnd_loc, "w") as outfile:
        for line in commands:
            outfile.write(line + "\n")


def cp_command(pipeline, load_data, output_location):
    """
    create cellprofiler commands

    Parameters:
    -----------
    pipeline: string
        path to cellprofiler pipeline
    load_data: string
        path to csv file suitable to Cellprofiler's LoadData module
    output_location: string
        where to store the results from the cellprofiler job

    Returns:
    --------
    string: a cellprofiler command
    """
    return "cellprofiler -r -c -p {pipeline} --data-file={load_data} -o {output_location}".format(
        pipeline=pipeline,
        load_data=load_data,
        output_location=output_location)


def make_output_directories(location):
    """
    create the directories to store the output, used in job.Job()

    Parameters:
    -----------
    location: string
        path to directory, this is the location in which the images will
        be staged, loaddata csv files stored, filelists and output
        data from the cellprofiler job will be stored.

    Returns:
    --------
    nothing, creates empty directories
    """
    for direc in ["loaddata", "raw_data", "logfiles"]:
        utils.make_dir(os.path.join(location, direc))
    # then make sub-directories in the logfile directory
    for subdirec in ["analysis"]:
        utils.make_dir(os.path.join(location, "logfiles", subdirec))


def check_commands(location):
    """
    Check commands files are not empty, raise an Error if they are.

    Parameters:
    -----------
    location: string
        location of commands file

    Returns:
    --------
    None if successful, otherwise raises a RuntimeError if the file
    is empty.
    """
    n_lines = utils.count_lines_in_file(location)
    err_msg = "Commands file '{}' is empty, something has gone wrong".format(location)
    if n_lines < 1:
        raise RuntimeError(err_msg)

