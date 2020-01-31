import os
import yaml


class Config:
    """class for cptools2 configuration"""
    def __init__(self, path_to_yaml):
        self.yaml_path = path_to_yaml
        self.config_dict = self.open_yaml()
        self.check_config()
        self.experiment = self.get_experiment()
        self.location = self.get_location()
        self.commands_location = self.get_commands_location()
        self.chunk = self.get_chunk()
        self.add_plate = self.get_add_plate()
        self.remove_plate = self.get_remove_plate()
        self.microscope = self.get_microscope()

    def open_yaml(self):
        with open(self.yaml_path, "r") as f:
            config_dict = yaml.load(f)
        return config_dict

    def check_config(self):
        valid_args = set([
            "experiment",
            "chunk",
            "pipeline",
            "location",
            "commands location",
            "remove plate",
            "add plate",
            "microscope"
        ])
        bad_arguments = []
        for argument in self.config_dict.keys():
            if argument not in valid_args:
                bad_arguments.append(argument)
        if len(bad_arguments) > 0:
            err_msg = "Invalid argument(s): {}".format(bad_arguments)
            raise ValueError(err_msg)

    def get_experiment(self):
        if "experiment" in self.config_dict:
            experiment_arg = self.config_dict["experiment"]
            if isinstance(experiment_arg, list):
                experiment_arg = experiment_arg[0]
            return experiment_arg

    def get_chunk(self):
        if "chunk" in self.config_dict:
            chunk_arg = self.config_dict["chunk"]
            if isinstance(chunk_arg, list):
                chunk_arg = chunk_arg[0]
            return int(chunk_arg)

    def get_add_plate(self):
        if "add plate" in self.config_dict:
            add_plate_dicts = self.config_dict["add plate"]
            # returns a list of dictionaries
            if isinstance(add_plate_dicts, list):
                for d in add_plate_dicts:
                    if "experiment" in d.keys():
                        # is the experiment label
                        experiment = str(d["experiment"])
                    if "plates" in d.keys():
                        # is the plates, either a string or a list
                        plate_args = d["plates"]
                        if isinstance(plate_args, str):
                            plates = [d["plates"]]
                        if isinstance(plate_args, list):
                            plates = d["plates"]
            return {"exp_dir": experiment, "plates": plates}

    def get_remove_plate(self):
        # can either be a string or a list in Job.remove_plate
        return self.config_dict.get("remove plate")

    def get_microscope(self):
        return self.config_dict.get("microscope")

    def get_pipeline(self):
        if "pipeline" in self.config_dict:
            pipeline_arg = self.config_dict["pipeline"]
            if isinstance(pipeline_arg, list):
                pipeline_arg = pipeline_arg[0]
            pipeline_arg = os.path.abspath(pipeline_arg)
            if not os.path.isfile(pipeline_arg):
                raise IOError("'{}' pipeline not found".format(pipeline_arg))
            return pipeline_arg

    def get_location(self):
        if "location" in self.config_dict:
            location_arg = self.config_dict["location"]
            if isinstance(location_arg, list):
                location_arg = location_arg[0]
        return location_arg

    def get_commands_location(self):
        if "commands location" in self.config_dict:
            commands_location_arg = self.config_dict["commands location"]
            if isinstance(commands_location_arg, list):
                commands_location_arg = commands_location_arg[0]
        return commands_location_arg

    def create_command_args(self):
        pipeline = self.get_pipeline()
        location = self.get_location()
        commands_location = self.get_commands_location()
        job_size = self.chunk
        command_args = {
            "pipeline": pipeline,
            "location": location,
            "commands_location": commands_location,
            "job_size": job_size
        }
        return command_args

    def parse(self):
        raise NotImplementedError()

