"""
Created by: Michael Kuczynski
Created on: June 18th, 2022
"""
from collections import namedtuple

from pathlib import Path
import os
import sys

import SimpleITK as sitk
import numpy as np
from py_aimio import read_aim, read_isq
from function_helpers import sitk_to_np, np_to_sitk

from ormir_xct.core.util.sitk_itk import itk_sitk

"""
Convenience tuple to hold a numpy image and its metadata. The metadata is a dictionary that can contain any information about the image, 
and can be updated by image manipulation functions using the "Processlog" decorator (@TODO implentation pending).
"""
NumpyImageTuple = namedtuple("NumpyImageTuple", ["image", "metadata"])

file_extensions = [".nii", ".mha", ".nrrd", ".aim", ".isq"]


def file_reader(input_file_path, as_numpy=False, **kwargs):
    """
    Read the input file using the correct reader. MHA/NII images can be read using SimpleITK.
    HR-pQCT (Scanco) AIM and ISQ images can be read using the py_aimio library.
    
    The function will return a SimpleITK image or a NumpyImageTuple depending on the as_numpy parameter.

    Optional keyword arguments can be passed to the `aimio.read_aim` function, such as `density` or `hu`.

    Parameters
    ----------
    input_file_path : string
        Path to the input file to be read.
    
    as_numpy : bool, optional
        If True, the image will be returned as a numpy array, and metadata will be returned as a dictionary. If False, it will be returned as a SimpleITK image.
        Default is False.

    Returns
    -------
    image : SimpleITK.Image or NumpyImageTuple
    """
    # check if the input file path is a `Path` object, if not convert it to a `Path` object
    if not isinstance(input_file_path, Path):
        input_file_path = Path(input_file_path)
        if not input_file_path.exists():
            raise FileNotFoundError(f"Input file {input_file_path} does not exist.")

    # Get the file extension and check if we can read it
    # input_filename = input_file_path.basename
    input_extension = input_file_path.suffix

    input_extension = input_extension.lower()
    
    if input_extension in file_extensions:
        if input_extension == ".aim" or input_extension == ".isq":
            # If the input AIM contains a version number, remove it and rename the file
            if ";" in input_extension:
                scanco_filename = input_file_path.rsplit(";", 1)[0]
                os.rename(input_file_path, scanco_filename)
                input_file_path = scanco_filename

            # Read the image using aimio
            if input_extension == ".aim":
                image, metadata = read_aim(input_file_path, **kwargs)
            else:
                image, metadata = read_isq(input_file_path, **kwargs)
            
            if as_numpy:
                return NumpyImageTuple(image, metadata)
        
            return np_to_sitk(image, metadata)
        else:
            image = sitk.ReadImage(input_file_path, sitk.sitkFloat32)
            if as_numpy:
                return sitk_to_np(image)
            return image
            
    else:
        raise ValueError(f"Input file {input_file_path} has an unsupported file extension. Supported extensions are: {file_extensions}")


def verify_image(input_image, precision=None):
    """
    Provide with string path or sitk.Image. Ensures string paths are converted to sitk.Image before processing.
    Avoid using for masks as the file_reader method uses sitk.sitkFloat32 precision.

    Parameters
    ----------
    input_image : string path to an sitk readable image or an sitk.Image
    precision: set precision if desired, None by default

    Returns
    -------
    image : SimpleITK.Image
    """

    if isinstance(input_image, str):
        return file_reader(input_image)
    else:
        return sitk.Cast(input_image, precision) if precision else input_image
