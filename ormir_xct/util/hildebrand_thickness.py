# -------------------------------------------------------#
# Created by: Nathan Neeteson
# Created on: ??
#
# Description: A set of utilities for morphometry on an
#               image and/or binary mask.
#
# -------------------------------------------------------#

from __future__ import annotations

import numpy as np
from collections.abc import Iterable
from numba import jit
from SimpleITK import GetImageFromArray, GetArrayFromImage, SignedMaurerDistanceMap
from skimage.morphology import skeletonize_3d
from typing import Union

# constant to add to denominator(s) to prevent divide-by-zero errors
EPS = 1e-8


@jit(nopython=True, fastmath=True)
def compute_local_thickness_from_distance_ridge(
    local_thickness: np.ndarray, dist_ridge: np.ndarray, voxel_width: np.ndarray
) -> np.ndarray:
    """
    Use Hildebrand's sphere-fitting method to compute the local thickness field for a
    binary image, given an array to fill in and the sorted distance ridge of the binary image.

    Since the ridge is sorted by distance values in ascending order, we can iterate through and assign ech voxel's
    distance value to all voxels within that distance. Voxels corresponding to larger spheres will be processed
    later and overwrite values assigned by smaller spheres, and so each voxel will eventually be assigned the
    diameter of the largest sphere that it lies within.

    Finally, we do not check every voxel in the image for whether it lies within a sphere. We only check voxels that
    lie within the cube with side length equal to the sphere diameter around the center voxel. This saves a lot of
    computational effort.

    Parameters
    ----------
    local_thickness : np.ndarray
        A numpy array that is initialized as zeros.

    dist_ridge : np.ndarray
        A numpy array that is the sorted distance ridge of a mask. Each row in this array is one voxel on the distance
        ridge, and in each row the first element should be the value of the distance transform while the next three
        elements are the i, j, and k indices of the location of that ridge voxel in the binary image.

    voxel_width : np.ndarray
        A numpy array with shape (3,) that gives the width of voxels in each dimension.

    Returns
    -------
    np.ndarray
        The local thickness field.
    """
    for (rd, ri, rj, rk) in dist_ridge:
        for di in range(
            np.maximum(np.floor(ri - rd/voxel_width[0]) - 1, 0),
            np.minimum(np.ceil(ri + rd/voxel_width[0]) + 1, local_thickness.shape[0]),
        ):
            for dj in range(
                np.maximum(np.floor(rj - rd/voxel_width[1]) - 1, 0),
                np.minimum(np.ceil(rj + rd/voxel_width[1]) + 1, local_thickness.shape[1]),
            ):
                for dk in range(
                    np.maximum(np.floor(rk - rd/voxel_width[2]) - 1, 0),
                    np.minimum(np.ceil(rk + rd/voxel_width[2]) + 1, local_thickness.shape[2]),
                ):
                    if (
                        (voxel_width[0] * (di - ri)) ** 2
                        + (voxel_width[1] * (dj - rj)) ** 2
                        + (voxel_width[2] * (dk - rk)) ** 2
                    ) < (rd ** 2):
                        local_thickness[di, dj, dk] = 2 * rd
    return local_thickness


def compute_local_thickness_from_mask(mask: np.ndarray, voxel_width: Union[Iterable[float], float]) -> np.ndarray:
    """
    Compute the local thickness field for a binary mask.

    This is done by calculating the distance transform and skeletonization, then combining these to create a sorted
    "distance ridge," which is an array of the distance transform values and indices of the skeletonization.
    Finally, a `numba`-jit-decorated function is called to efficiently use Hildebrand's sphere-fitting method for
    local thickness calculation. The local thickness field is scaled by the voxel width and multiplied by the
    binary mask to ensure local thickness values are not assigned to the background inadvertently.

    Parameters
    ----------
    mask : np.ndarray
        The mask for which to calculate the local thickness field.

    voxel_width : Union[Iterable[float], float]
        If an iterable of length 3, the voxel widths in each dimension. If a float, the isotropic voxel width.

    Returns
    -------
    np.ndarray
        The local thickness field.
    """
    if isinstance(voxel_width, float) or isinstance(voxel_width, int):
        voxel_width = np.array([float(voxel_width)]*3)
    elif isinstance(voxel_width, Iterable):
        if len(voxel_width) != 3:
            raise ValueError("`voxel_width must be a float, int, or iterable of length 3`")
        else:
            voxel_width = np.array(voxel_width).astype(float)
    else:
        raise ValueError("`voxel_width must be a float, int, or iterable of length 3`")

    mask_sitk = GetImageFromArray(mask.astype(int))
    mask_sitk.SetSpacing(tuple(voxel_width))
    mask_dist = mask * GetArrayFromImage(SignedMaurerDistanceMap(
        mask_sitk, useImageSpacing=True, insideIsPositive=True, squaredDistance=False
    ))
    ridge = [(mask_dist[i, j, k], i, j, k) for (i, j, k) in zip(*(skeletonize_3d(mask).nonzero()))]
    ridge.sort()
    local_thickness = compute_local_thickness_from_distance_ridge(
        np.zeros(mask.shape, dtype=float), np.array(ridge), voxel_width
    )
    return (mask > 0) * local_thickness


def calc_structure_thickness_statistics(mask: np.ndarray, voxel_width: Union[float, Iterable], min_thickness: float):
    """
    Parameters
    ----------
    mask : numpy.ndarray
        3-dimensional numpy array containing a binary mask that is the segmentation of the structure you want
        to calculate the mean thickness of

    voxel_width : Union[float, Iterable]
        physical width of a voxel, for scaling distance. Either a single float value or length-3 iterable

    min_thickness : float
        the minimum thickness of the structure you want to calculate the mean thickness of

    Returns
    -------
    tuple
        the mean, standard deviation, minimum, and maximum of the local thickness of the structure defined by the mask,
        and the whole local thickness field of the entire image (0 outside the mask)
    """

    local_thickness = compute_local_thickness_from_mask(mask, voxel_width)
    local_thickness_structure = local_thickness[mask > 0]

    local_thickness_structure = np.maximum(local_thickness_structure, min_thickness)

    return (
        local_thickness_structure.mean(),
        local_thickness_structure.std(),
        local_thickness_structure.min(),
        local_thickness_structure.max(),
        local_thickness,
    )