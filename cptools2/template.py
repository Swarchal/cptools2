import textwrap

def print_template():
    print(textwrap.dedent("""
        experiment: # path to experiment containing images

        pipeline: # path to cellprofiler pipeline

        microscope: # which microscope captured the images in experiment

        location: # where to store the loaddata and log files

        commands_location: # where to store the SGE commands

        chunk: # how many images per task

        channels:
            - 1: # name of channel number 1
            - 2: # name of channel number 2
    """))
