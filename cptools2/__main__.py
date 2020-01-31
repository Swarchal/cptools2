import sys
import os
import textwrap
from cptools2 import generate_scripts
from cptools2 import job
from cptools2 import parse_config
from cptools2 import utils
from cptools2 import colours
from cptools2.colours import pretty_print, green


def check_arguments():
    """docstring"""
    if len(sys.argv) < 2:
        msg = "missing argument: need to pass a config file as an argument"
        raise ValueError(msg)


def configure_job(config):
    """
    configure job to generate the commands and scripts

    Parameters:
    ------------
    config: namedtuple
        config namedtuple containing the dictionaries which are
        passed as arguments via **kwargs to the Job class.

    Returns:
    ---------
    nothing, saves commands and scripts to disk
    """
    jobber = job.Job(config.microscope)
    # some of the optional arguments might be none if that option was not present in the
    # configuration file, in which case don't pass them as arguments to the methods
    if config.experiment is not None:
        jobber.add_experiment(config.experiment)
    if config.remove_plate is not None:
        jobber.remove_plate(config.remove_plate)
    if config.add_plate is not None:
        jobber.add_plate(**config.add_plate)
    if config.chunk is not None:
        jobber.chunk(config.chunk)
    jobber.create_commands(**config.create_command_args())


def make_scripts(config):
    """
    creates the qsub scripts

    Parameters:
    -----------
    config_file: cptools.parse_config.Config

    Returns:
    ---------
    nothing
    """
    commands_line_count = generate_scripts.lines_in_commands(config.commands_location)
    logfile_location = os.path.join(config.location, "logfiles")
    generate_scripts.make_qsub_scripts(
       config.commands_location,
        commands_line_count,
        logfile_location=logfile_location
    )


def main():
    """run cptools.job.Job on a yaml file containing arguments"""
    print(green(textwrap.dedent("""\
      ___ ___ _____ ___   ___  _    ___ ___
     / __| _ \_   _/ _ \ / _ \| |  / __|_  )
    | (__|  _/ | || (_) | (_) | |__\__ \/ /
     \___|_|   |_| \___/ \___/|____|___/___|
    """)))
    check_arguments()
    # parse yaml file into a dictionary
    path_to_config = sys.argv[1]
    config = parse_config.Config(path_to_config)
    pretty_print("parsing config file {}".format(colours.yellow(path_to_config)))
    configure_job(config)
    pretty_print("creating SGE script")
    make_scripts(config)
    pretty_print("DONE!")


if __name__ == "__main__":
    main()
