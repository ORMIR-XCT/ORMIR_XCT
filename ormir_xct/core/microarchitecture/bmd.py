"""
bmd.py

Created by:   Michael Kuczynski
Created on:   June 29, 2022

Description: Calculates Bone Mineral Density (BMD) of
             an image in mgHA/ccm. The user must specify
             what the input image's units are
             (e.g., HU, Scanco native, linear attenuation)

Notes:
  1. If using AIM/ISQ images as input, they are read in using
      the ITK Scanco reader which automatically converts the
      images from Scanco native units to HU.
  2. If using NII/MHA/etc. images as input, they are read in
      using the SimpleITK reader and you need to know the 
      units of your image to provide as input.
  3. Default values are provided for muScaling, muWater, 
      rescaleSlope, and rescaleIntercept, but you should
      try to provide your own values for improved accuracy.

Usage:
  python bmd.py inputImage.nii
  python bmd.py inputImage.AIM HU 8192 0.2396 1613.94397 -392.247009
"""
import sys
import SimpleITK as sitk

from ormir_xct.core.util.hrpqct_rescale import (
    convert_native_to_bmd,
    convert_linear_attenuation_to_bmd,
    convert_hu_to_bmd,
)
from ormir_xct.core.util.file_reader import verify_image


def bmd(
    image, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept
):
    """
    Compute bone mineral density (BMD) from the intensity information of the
    provided image. The image units need to be provided to convert voxels to
    BMD units (mg HA/ccm) before calculating BMD.

    Parameters
    ----------
    image : SimpleITK.Image

    image_units : string

    mu_scaling : int

    mu_water : float

    rescale_slope : float

    rescale_intercept : float

    Returns
    -------
    image_statistics_filter : SimpleITK.StatisticsImageFilter
    """

    # TODO: Incorrect method docstring return?

    mean, std = 0, 0
    image = verify_image(image)

    # No conversion needed if we already have BMD units
    if image_units == "scanco":
        # Convert from Scanco native units to linear attenuation. Then convert to BMD.
        # Convert both the image and background value.
        image = convert_native_to_bmd(
            image, mu_scaling, rescale_slope, rescale_intercept
        )
    elif image_units == "attenuation":
        # Convert to BMD.
        # Convert both the image and background value.
        image = convert_linear_attenuation_to_bmd(
            image, rescale_slope, rescale_intercept
        )
    elif image_units == "hu":
        # Convert from HU to linear attenuation. Then convert to BMD.
        # Convert both the image and background value.
        image = convert_hu_to_bmd(image, mu_water, rescale_slope, rescale_intercept)
    elif image_units != "bmd":
        print(
            "ERROR: Invalid image units provided. Only BMD, SCANCO, ATTENUATION, or HU are accepted."
        )
        sys.exit(1)

    numpy_image = sitk.GetArrayFromImage(image)
    mean = numpy_image.mean()
    std = numpy_image.std()

    return mean, std


