import pandas as _pd
from cptools2 import parse_metadata


def _well_site_table(img_list, microscope="imagexpress"):
    """
    parse metadata from image paths and return a pandas dataframe
    of image_path and metadata columns

    Parameters:
    -----------
    img_list: list
        list of image paths
    microscope: string
        type of microscope the images come from

    Returns:
    --------
    pandas DataFrame of img_paths and Metadata_well, Metadata_site columns
    """
    parser = parse_metadata.MetadataParser(microscope)
    df_img = _pd.DataFrame(
        parser.parse_filepath_list(img_list)
    )
    df_img = df_img[["Metadata_well", "Metadata_site"]]
    df_img["path"] = img_list
    return df_img


def _group_images(df_img, microscope="imagexpress"):
    """
    group a single dataframe into a list of dataframes, with a dataframe
    per well and site

    Parameters:
    -----------
    df_img: pandas.DataFrame
        dataframe containing image paths with well and site metadata columns

    microscope: string
        type of microscope the images come from

    Returns:
    --------
    a list of pandas DataFrames, grouped by well and site
    """
    parser = parse_metadata.MetadataParser(microscope)
    grouped_list = []
    for _, group in  df_img.groupby(["Metadata_well", "Metadata_site"]):
        grouped = list(group["path"])
        channel_nums = [parser.parse_channel(i) for i in grouped]
        # create tuple (path, channel_number) and sort by channel number
        sort_im = sorted(list(zip(grouped, channel_nums)), key=lambda x: x[1])
        # return on the file-paths back from the list of tuples
        grouped_list.append([i[0] for i in sort_im])
    return grouped_list


def chunks(list_like, job_size):
    """
    generator to split list_like into job_size chunks

    Parameters:
    -----------
    list_like: list
    job_size: int
        how many elements in each chunk

    Returns:
    --------
    generator for returning a list of lists, each sub-list containing
    `job_size` elements (apart from the last sub-list which may contain
    fewer elements)
    """
    for i in range(0, len(list_like), job_size):
        yield list_like[i:i+job_size]


def split(img_list, job_size=96, microscope="imagexpress"):
    """
    split imagelist into an imagelist per job containing job_size images

    Parameters:
    -----------
    img_list: list
        list of image paths
    job_size: int (default = 96)

    Returns:
    --------
    list of dataframes
    """
    df_img = _well_site_table(img_list, microscope)
    grouped_list = _group_images(df_img, microscope)
    return [chunk for chunk in chunks(grouped_list, job_size)]
