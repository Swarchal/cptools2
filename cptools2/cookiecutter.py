"""
Automatically generate SGE submission scripts from a template.
"""

import os
import random
import subprocess
import textwrap


class SGEScript(object):
    """
    Base class for SGE submission scripts.
    Just the bare basics for an SGE submission without any actual code.

    Parameters:
    -----------
    name: string (default = randomly generated hex code)
        Name of the job.

    user: string (default = $USER from environment)
        Username on the cluster. This will be automatically detected if
        ran on the cluster. If ran locally then this will need to be supplied.


    output: string (default = /exports/eddie/scratch/$USER/)
        output location for stdout and stderr files, defaults to user's
        scratch space. This is just for the job output, i.e jobname.o1234568

    queue: string (default="lungo.q")
        queue to be used, has to be a valid option for -q

    runtime: string (optional)
        Run time limit for the job, has to be a valid parameter for `-l h_rt`.

    tasks: string, integer, or list of two integers. (optional)
        The command to be passed to `#$ -t`.
        `tasks` can be provided in a few formats
        - string: it is inserted into the template script.
        - int: taken as 1-int tasks
        - [int, int], taken as a range from int-int

    hold_jid: string. (optional)
        name of job which has to finish for this job to start running

    hold_jid_ad: string. (optional)
        name of array job, this array job will wait to the corresponding
        $SGE_TASK_ID in `hold_jid_ad` to finish running before starting
        that task.

    pe: string. (optional)
        parallel environment passed to `#$ -pe`


    Methods:
    --------

    loop_through_file:
        Adds text to template to loop through `input_file`, running a
        task for each line of `input_file` as an array job.

        Parameters:
        ------------
        intput_file: string
            path to file containing commands

        Returns:
        --------
        Nothing, adds text to template script in place.


    save:
        Save script to location specified in `path`

        Parameters:
        -------------
        path: string
            location to save the script


    submit:
        Submit script to job queue. Only works if script has been saved.

        Parameters:
        -----------
        none
    """

    def __init__(
        self,
        name=None,
        user=None,
        runtime=None,
        queue="lungo.q",
        output=None,
        tasks=None,
        hold_jid=False,
        hold_jid_ad=False,
        pe=None,
    ):
        self.name = generate_random_hex() if name is None else name
        self.user = get_user(user)
        self.runtime = runtime
        self.queue = queue
        self.save_path = None
        self.output = (
            "/scratch/{}/".format(self.user) if output is None else output
        )
        self.template = textwrap.dedent(
            """
            #!/bin/sh

            #$ -N {name}
            #$ -q {queue}
            #$ -o {output}
            #$ -j y
            """.format(
                name=self.name,
                queue=self.queue,
                output=self.output,
            )
        )
        if tasks is not None:
            self.tasks = parse_tasks(tasks)
            self.array = True
            self.template += "#$ -t {}\n".format(self.tasks)
        else:
            self.array = False
            self.tasks = None
        if runtime is not None:
            self.template += "#$ -l h_rt={}\n".format(self.runtime)
        if hold_jid is not False and hold_jid_ad is not False:
            raise ValueError("Cannot use both 'hold_jid' and 'hold_jid_ad'")
        if hold_jid is not False:
            self.template += "#$ -hold_jid {}\n".format(hold_jid)
        if hold_jid_ad is not False:
            self.template += "#$ -hold_jid_ad {}\n".format(hold_jid_ad)
        if pe is not None:
            self.template += "#$ -pe {}\n".format(pe)

    def __str__(self):
        return str(self.template)

    def __repr__(self):
        return "SGEScript: name={}, runtime={}, user={}".format(
            self.name, self.runtime, self.user
        )

    def __iadd__(self, right_side):
        self.template = self.template + textwrap.dedent("{}\n".format(right_side))
        return self

    def loop_through_file(self, input_file):
        """
        Add text to script template to loop through a file containing a
        command to be run on each line.

        This using an array job this will setup an awk command to run each
        line of according to the SGE_TASK_ID

        Parameters:
        -----------
        input_file: path to a file
            This file should contain multiple lines of commands.
            Each line will be run separately in an array job.

        Returns:
        --------
        Nothing, adds text to template script in place.
        """
        # if the number of tasks is not set, but we can read the input file
        # then automatically detect the number of lines in `input_file`
        # and set this value as `self.tasks`.
        if self.tasks is None and os.path.isfile(input_file):
            num_lines = get_num_lines(input_file)
            self.tasks = "#$ -t 1-{}".format(num_lines)
            self.template += self.tasks
            self.array = True
            print(
                "NOTE:{} tasks inferred from number of lines in {}".format(
                    num_lines, input_file
                )
            )
        # if the number of tasks if not given and we can't read `input_file`,
        # then the number of tasks cannot be set automatically, so raise a
        # ScriptError
        elif self.array is False and self.tasks is None:
            err_msg = "'tasks` was not set, and cannot read {}".format(input_file)
            raise ScriptError(err_msg)
        # one way of getting the line from `input_file` to match $SGE_TASK_ID
        text = """
               SEEDFILE="{input_file}"
               SEED=$(awk "NR==$SGE_TASK_ID" "$SEEDFILE")
               $SEED
               """.format(
            input_file=input_file
        )
        self.template += textwrap.dedent(text)

    def save(self, path):
        """save script/template to path"""
        with open(path, "w") as out_file:
            out_file.write(self.template + "\n")
        self.save_path = path

    def submit(self):
        """submit script to the job queue (if on a login node)"""
        if on_login_node():
            if self.save_path is None:
                raise SubmissionError("Need to save script before submitting")
            else:
                abs_save_path = os.path.abspath(self.save_path)
                return_code = subprocess.Popen(["qsub", abs_save_path]).wait()
                if return_code != 0:
                    raise SubmissionError("Job submission failed")
        else:
            raise SubmissionError("Cannot submit job, not on a login node.")

    def run(self):
        """alias for submit()"""
        self.submit()


def generate_random_hex():
    """
    Generate a random hex number.
    Lifted from stackoverflow
    """
    tmp = "0123456789abcdef"
    result = [random.choice("abcdef")] + [random.choice(tmp) for _ in range(4)]
    random.shuffle(result)
    # job names cannot start with a number
    # insert first character from the letters onwards
    result.insert(0, random.choice(tmp[10:]))
    return "".join(result)


def get_user(user):
    """
    - Return username. If passed a username then will simply return that.
    - If not given a user an an argument, then this will try and determine
      username from the environment variables (if running on the cluster).
    - Will raise a ValueError if not passed a user and not running on the
      cluster.
    """
    if user is not None:
        return user
    elif on_the_cluster():
        return os.environ["USER"]
    else:
        raise UserError(
            "No argument given for 'user' and not running on "
            "the cluster, therefore unable to automatically "
            "detect the username"
        )


def parse_tasks(tasks):
    """parse tasks argument, as it can accept any from: (str, int, list)"""
    if isinstance(tasks, str):
        return tasks
    if isinstance(tasks, list) and all(isinstance(i, int) for i in tasks):
        if len(tasks) == 2:
            tasks = "{}-{}".format(*tasks)
        else:
            msg = "'tasks' has to be either a list of length 2 or a str"
            raise ScriptError(msg)
    # if tasks is a single integer then we can take that as 1-tasks
    if isinstance(tasks, int):
        tasks = "1-{}".format(tasks)
    return tasks


def on_the_cluster():
    """
    Determine if script is currently running on the cluster or not.

    Returns: Boolean
    """
    try:
        keyname = os.environ["SGE_CLUSTER_NAME"]
    except KeyError:
        return False
    return keyname == "idrs"


def on_login_node():
    """
    Determine if we are on a login node, i.e not a compute or staging node, and
    capable of submitting jobs.

    This is done by checking the $HOSTNAME.
    """
    if on_the_cluster():
        return os.environ["HOSTNAME"] == "srsu476"
    else:
        return False


def get_num_lines(file_path):
    """
    Count number of lines in a file

    Parameters:
    -----------
    file_path: string
        path to file

    Returns:
    --------
    int: number of lines in file_path
    """
    with open(file_path, "r") as f:
        for i, _ in enumerate(f, 1):
            pass
    return i


class SubmissionError(Exception):
    pass


class ScriptError(Exception):
    pass

class UserError(Exception):
    pass
