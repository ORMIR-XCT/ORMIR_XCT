"""
gauss_seg.py

Created by:   Michael Kuczynski
Created on:   June 29, 2022

Description: Binarize an input image following the standard
              segmentation protocol performed in IPL. 

Notes:
  1. Gaussian smoothing is done in IPL with sigma = 0.5
      and support = 1. In ITK, this translates to using
      the SmoothingRecursiveGaussian filter with
      sigma = 0.5 * voxel size = 0.5 * 0.0606964.
  2. The output of the Guassian filter will be a float
      image so we may need to cast to a different type
      depending on what image you want to write to.
  3. The binarization is done using the same thresholds
      set in IPL, but we need to know the image units
      prior to binarization (default is set to BMD units).
"""

import sys
import argparse
import SimpleITK as sitk

from ormir_xct.util.scanco_rescale import *

# Default threshold values used in IPL
threshold_dict = {
    "HU_Lower": 1170.0,
    "HU_Upper": 10000.0,
    "BMD_Lower": 446.8,
    "BMD_Upper": 3000.0,
    "Native_Lower": 4259.0,
    "Native_Upper": 32767.0,
    "LinAtt_Lower": 0.52,
    "LinAtt_Upper": 4.00,
    "Per1000_Lower": 130.0,
    "Per1000_Upper": 1000.0,
}

# gauss_seg / ipl_seg
def gauss_seg(
    input_image,
    lower_threshold,
    upper_threshold,
    value_in_range=127,
    voxel_size=0.0606964,
    sigma=0.5,
):
    """
    Check the image units and get the correct thresholds.

    Parameters
    ----------
    input_image : SimpleITK.Image

    lower_threshold : int

    upper_threshold : int

    value_in_range : int

    voxel_size : float

    sigma : float

    Returns
    -------
    seg : SimpleITK.Image
    """
    smooth = sitk.SmoothingRecursiveGaussian(input_image, sigma * voxel_size)
    seg = sitk.BinaryThreshold(
        smooth, lower_threshold, upper_threshold, value_in_range, 0
    )
    return seg


