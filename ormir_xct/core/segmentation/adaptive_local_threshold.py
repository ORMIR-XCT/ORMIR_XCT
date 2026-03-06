"""
Created by: Michael Kuczynski
Created on: June 9th, 2022

Adapted from the adaptive_local_thresholding.py script from the Bone Imaging Lab at 
the University of Calgary: https://github.com/Bonelab/Bonelab

Description: Contains functions to obtain joint space
            segmentation masks using the standard
            IPL implementation (translated to Python).
"""

import numpy as np
import SimpleITK as sitk

from scipy import ndimage
from skimage.filters import gaussian
from skimage.morphology import ball, remove_small_objects, footprint_rectangle
from concurrent.futures import ThreadPoolExecutor

from ormir_xct.core.util.file_reader import verify_image

def compute_minmax_threshold_image(
    density: np.ndarray, 
    footprint: np.ndarray,
) -> np.ndarray:
    """
    Calculate the minmax threshold image.

    Parameters
    ----------
    density : np.ndarray
        The density image to be thresholded.

    footprint : np.ndarray
        The footprint to use for identifying local thresholds.

    
    Returns
    -------
    np.ndarray
        The minmax threshold image.
    """

    print("Calculating max image...")
    max_image = ndimage.maximum_filter(density, footprint=footprint)
    print("Calculating min image...")
    min_image = ndimage.minimum_filter(density, footprint=footprint)
    print("Calculating minmax threshold image...")
    return (min_image + max_image) / 2


def compute_mean_threshold_image(
    density: np.ndarray, 
    footprint: np.ndarray,
) -> np.ndarray:
    """
    Calculate the mean threshold image.

    Parameters
    ----------
    density : np.ndarray
        The density image to be thresholded.

    footprint : np.ndarray
        The footprint to use for identifying local thresholds.


    Returns
    -------
    np.ndarray
        The mean threshold image.
    """
    print("Calculating mean image...")
    return ndimage.convolve(density, footprint / footprint.sum())


def compute_adaptive_local_threshold_segmentation(
    density: np.ndarray,
    low_threshold: float,
    high_threshold: float,
    footprint: np.ndarray,
    mode: str,
    sigma: float,
    min_size: int,
) -> np.ndarray:
    """
    Perform local adaptive thresholding on a density image.

    Parameters
    ----------
    density : np.ndarray
        The density image to be thresholded.

    low_threshold : float
        The lower threshold for the density image.

    high_threshold : float
        The upper threshold for the density image.

    footprint : np.ndarray
        The footprint to use for identifying local thresholds.

    mode : str
        The mode to use for identifying local thresholds. Can be `mean`, `minmax`, or `both`.

    sigma : float
        The sigma to use for the gaussian filter.

    min_size : int
        The minimum size of structures to keep in the segmentation.

    Returns
    -------
    np.ndarray
        The thresholded image.
    """
    print(f"Calculating threshold image using mode: {mode}")

    if mode == "mean":
        threshold_image = compute_mean_threshold_image(density, footprint)
    elif mode == "minmax":
        threshold_image = compute_minmax_threshold_image(density, footprint)
    elif mode == "both":
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_mean = executor.submit(
                compute_mean_threshold_image, density, footprint
            )
            future_minmax = executor.submit(
                compute_minmax_threshold_image, density, footprint
            )
            threshold_image = np.minimum(future_mean.result(), future_minmax.result())
    else:
        raise ValueError(
            f"`mode` must be one of `mean`, `minmax`, or `both`, received {mode}."
        )

    if sigma != None:
        density = gaussian(density, sigma=sigma)

    return remove_small_objects(
        ((density > low_threshold) & (density > threshold_image))
        | (density > high_threshold),
        min_size=min_size,
    )


def adaptive_local_thresholding(
    image_sitk,
    structuring_element_shape,
    structuring_element_size,
    lower_threshold,
    upper_threshold,
    local_threshold_method,
    sigma,
    minimum_structure_size,
):
    """
    Perform local adaptive thresholding on input image.

    Parameters
    ----------
    image_sitk : sitk.Image or str
        Image to threshold, accepts string paths.

    structuring_element_shape : str
        Shape of the structuring element, accepts "ball" or "cube".
    
    structuring_element_size : int
        Size of structuring element.

    lower_threshold : float
        The lower threshold.

    upper_threshold : float
        The upper threshold.

    local_threshold_method : str
        The method to use for identifying local thresholds. Accepts "mean", "minmax", or "both"

    sigma : float
        The sigma to use for the gaussian filter.

    minimum_structure_size : int
        The minimum size of structures to keep in the segmentation.

    Returns
    -------
    sitk.Image
        The thresholded image.
    """

    # Handle string paths
    image_sitk = verify_image(image_sitk)

    image = sitk.GetArrayFromImage(image_sitk)

    if structuring_element_shape == "ball":
        footprint = np.asarray(ball(structuring_element_size))
    elif structuring_element_shape == "cube":
        # cube is depreciated and will be removed. Recommended to use footprint_rectangle instead
        # using shape (structuring_element_size,) * 3 produces a 3 dimensional cube 
        footprint = np.asarray(footprint_rectangle((structuring_element_size, ) * 3))
    else:
        raise ValueError("Invalid structuring element shape.")
    
    segmentation = compute_adaptive_local_threshold_segmentation(
        image,
        lower_threshold,
        upper_threshold,
        footprint,
        local_threshold_method,
        sigma,
        minimum_structure_size,
    )
    segmentation_sitk = sitk.GetImageFromArray(segmentation.astype(int))
    segmentation_sitk.CopyInformation(image_sitk)

    return segmentation_sitk
