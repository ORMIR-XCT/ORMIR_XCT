"""
function_helpers.py

Created by:   Johannes Bereiter-Payr
Created on:   09-07-2026

Description: Helper functions for image processing pipeline
"""

import numpy as np
import SimpleITK as sitk

from file_reader import file_reader

def ensure_np(image, metadata=None):
    """
    Ensure that the input image is a numpy array. If it is a SimpleITK image, convert it to a numpy array.
    If it is a string path, read the image and convert it to a numpy array.

    If a metadata dictionary is provided, it will be updated with the metadata from the SimpleITK image.

    Parameters
    ----------
    image : SimpleITK.Image or np.ndarray

    Returns
    -------
    np.ndarray
    """
    if isinstance(image, str):
        image = file_reader.read_image(image)

    if isinstance(image, sitk.Image):
        return sitk_to_np(image, metadata)
    elif isinstance(image, np.ndarray):
        return image
    else:
        raise TypeError("Input must be a SimpleITK image or a numpy array.")
    
def ensure_sitk(image, metadata=None):
    """
    Ensure that the input image is a SimpleITK image. If it is a numpy array, convert it to a SimpleITK image.
    If it is a string path, read the image and convert it to a SimpleITK image.
    
    If a metadata dictionary is provided, the SimpleITK image will be updated with the metadata from the dictionary.

    Parameters
    ----------
    image : np.ndarray or SimpleITK.Image

    Returns
    -------
    SimpleITK.Image
    """
    if isinstance(image, str):
        image = file_reader.read_image(image)

    if isinstance(image, np.ndarray):
        return np_to_sitk(image, metadata)
    elif isinstance(image, sitk.Image):
        return image
    else:
        raise TypeError("Input must be a numpy array or a SimpleITK image.")
    
def sitk_to_np(image, metadata=None):
    """
    Convert a SimpleITK image to a numpy array.

    Parameters
    ----------
    image : SimpleITK.Image

    Returns
    -------
    np.ndarray
    """
    if not isinstance(image, sitk.Image):
        raise TypeError("Input must be a SimpleITK image.")
    
    _metadata = {key: image.GetMetaData(key) for key in image.GetMetaDataKeys()}
    
    if metadata is not None:
        metadata.update(_metadata)
        return sitk.GetArrayFromImage(image)
    
    return sitk.GetArrayFromImage(image), metadata

def np_to_sitk(array, metadata=None):
    """
    Convert a numpy array to a SimpleITK image.

    Parameters
    ----------
    array : np.ndarray

    Returns
    -------
    SimpleITK.Image
    """
    if not isinstance(array, np.ndarray):
        raise TypeError("Input must be a numpy array.")
    
    sitk_image = sitk.GetImageFromArray(array)
    
    if metadata is not None:
        for key, value in metadata.items():
            sitk_image.SetMetaData(key, str(value))
    
    return sitk_image