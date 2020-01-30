import glob
import os

from cptools2 import utils


class Filelist:
    def __init__(self, microscope):
        self.microscope = microscope
        self.filelist_map = {
            "imagexpress": ImageXpress,
            "yokogawa": Yokogawa,
            "opera": Opera
        }
        self.filelist_micro = self.filelist_map[microscope]()

    def files_from_plate(self, plate_dir):
        return self.filelist_micro.files_from_plate(plate_dir)

    def paths_to_plates(self, exp_dir):
        return self.filelist_micro.paths_to_plates(exp_dir)

    def clean_filelist(self, filelist):
        return self.filelist_micro.clean_filelist(filelist)


class Micro:
    """abstract class for Microscope filelist"""
    def __init__(self):
        self.ext = ".tif"

    def files_from_plate(self):
        raise NotImplementedError

    def clean_filelist(self):
        raise NotImplementedError

    def paths_to_plates(self, experiment_directory):
        """
        Return the absolute file path to all plates contained within
        an ImageXpress experiment directory.

        Parameters:
        -----------
        experiment_directory: string
            Path to top-level experiment in the ImageXpress directory.
            This should contain sub-directories of plates.

        Returns:
        --------
        list of fully-formed paths to the plate directories.
        """
        exp_abs_path = os.path.abspath(experiment_directory)
        # check the experiment directory exists
        if not os.path.isdir(exp_abs_path):
            err_msg = "'{}' directory not found".format(exp_abs_path)
            raise RuntimeError(err_msg)
        plates = os.listdir(experiment_directory)
        plate_paths = [os.path.join(exp_abs_path, plate) for plate in plates]
        return [path for path in plate_paths if os.path.isdir(path)]

    @staticmethod
    def check_filelist_len(filelist, plate_dir):
        if len(filelist) == 0:
            err_msg = "No files found in '{}'".format(plate_dir)
            raise RuntimeError(err_msg)

    @staticmethod
    def check_dir_exists(directory):
        if not os.path.isdir(directory):
            raise RuntimeError("'{}' is not a plate directory".format(directory))


class ImageXpress(Micro):
    """ImageXpress specific filelist creator"""
    def __init__(self):
        super(ImageXpress, self).__init__()

    def files_from_plate(self, plate_dir):
        """
        return all proper image files from a plate directory

        Parameters:
        -----------
        plate_dir : string
            path to plate directory
        """
        self.check_dir_exists(plate_dir)
        files = glob.glob(plate_dir + "/*/*/*" + self.ext)
        files = self.clean_filelist(filelist=files)
        files = [os.path.join(*i.split(os.sep)[-4:]) for i in files]
        self.check_filelist_len(files, plate_dir)
        return files

    def clean_filelist(self, filelist):
        new_filelist = []
        for i in filelist:
            if i.endswith(self.ext) and "thumb" not in i:
                new_filelist.append(i)
        return new_filelist


class Yokogawa(Micro):
    """Yokogawa CV8000 specific filelist creator"""
    def __init__(self):
        super(Yokogawa, self).__init__()

    def files_from_plate(self, plate_dir):
        self.check_dir_exists(plate_dir)
        all_img_files = glob.glob(plate_dir + "/*" + self.ext)
        files = self.clean_filelist(all_img_files)
        self.check_filelist_len(files, plate_dir)
        return files

    def clean_filelist(self, filelist):
        new_filelist = []
        for f in filelist:
            if f.endswith(".tif"):
                if "CAM#" not in f:
                    if "_M01_CH" not in f:
                        new_filelist.append(f)
        return new_filelist


class Opera(Micro):
    """Opera Phenix specific filelist creator"""
    def __init__(self):
        super(Opera, self).__init__()

    def files_from_plate(self):
        pass

    def clean_filelist(self):
        pass

